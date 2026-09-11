"""Semantic validation and production gates for public run records."""

from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Iterable

from .canonical import source_digest
from .authority import require_registered_approval
from .artifacts import verify_raster_asset
from .errors import ApprovalError, ProductionGateError, PublisherError
from .schema import (
    validate_action_schema,
    validate_approval_schema,
    validate_manifest_schema,
    validate_public_projection,
    validate_timeline_schema,
)
from .security import checked_path, inspect_artifact_root, reject_forbidden_fields, require_approved_text_uris, safe_public_url


REQUIRED_APPROVAL_FIELDS = {
    "schema_version",
    "public_run_id",
    "title",
    "recorded_at",
    "publication_version",
    "classification",
    "evidence_kind",
    "outcome",
    "model_configuration",
    "game_configuration",
    "observation_policy",
    "seed_policy",
    "resource_budget",
    "intervention",
    "evidence",
    "action_timeline",
    "evidence_context",
    "decision_card",
    "case_study",
    "local_guess_reveal",
    "approval_reference",
    "disclosures",
    "test_fixture",
}


def _parse_datetime(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise PublisherError(f"invalid {field} timestamp") from exc
    if parsed.tzinfo is None:
        raise PublisherError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Validate schema and cross-field safety invariants."""

    reject_forbidden_fields(manifest)
    validate_manifest_schema(manifest)
    validate_manifest_integrity(manifest)
    return manifest


def validate_manifest_integrity(manifest: dict[str, Any]) -> None:
    expected = source_digest(manifest)
    declared = manifest["source"]["content_digest"]
    if declared != expected:
        raise PublisherError(
            "source.content_digest does not match the canonical sanitized manifest; any edited source invalidates approval"
        )

    timeline = manifest["action_timeline"]
    validate_timeline_schema(timeline)
    if timeline["public_run_id"] != manifest["public_run_id"]:
        raise PublisherError("action timeline belongs to a different public run")
    decisions = timeline["decisions"]
    references = manifest["source"]["references"]
    labels = [reference["label"] for reference in references]
    if len(labels) != len(set(labels)):
        raise PublisherError("source reference labels must be unique")
    for reference in references:
        safe_public_url(reference["uri"])
    context_reference = manifest["evidence_context"]["source_reference"]
    if context_reference is not None and context_reference not in labels:
        raise PublisherError("evidence context must point to an included source reference")
    seen_ids: set[str] = set()
    sequences: list[int] = []
    for decision in decisions:
        validate_action_schema(decision)
        if decision["public_run_id"] != manifest["public_run_id"]:
            raise PublisherError("action decision belongs to a different public run")
        if decision["decision_id"] in seen_ids:
            raise PublisherError("duplicate public decision ID")
        seen_ids.add(decision["decision_id"])
        sequences.append(decision["sequence"])
        explanation_reference = (decision["explanation"] or {}).get("source_reference")
        if explanation_reference is not None and explanation_reference not in labels:
            raise PublisherError("decision explanation must point to an included source reference")
        timing = decision["timing"]
        if timing is not None and timing["captured"] != (timing["media_offset_ms"] is not None):
            raise PublisherError("captured timing requires a media offset and uncaptured timing forbids one")
        choices = decision["legal_choices"]
        selected = decision["chosen_action"]
        if decision["state_visibility"] == "approved" and selected is not None and choices and selected not in choices:
            raise PublisherError("chosen action is not one of the approved legal choices")
        if decision["state_visibility"] == "redacted" and decision["state_summary"] is not None:
            raise PublisherError("redacted state may not carry a state summary")
        if decision["decision_card"] and decision["decision_card"]["status"] == "available":
            card = decision["decision_card"]
            if not card["asset_id"] or not card["artifact_digest"] or not card["provenance_reference"]:
                raise PublisherError("an available decision card needs complete artifact lineage")
            safe_public_url(card["provenance_reference"])
    if sequences != sorted(sequences) or len(set(sequences)) != len(sequences):
        raise PublisherError("action sequence values must be strictly increasing")
    if timeline["status"] == "unavailable" and decisions:
        raise PublisherError("unavailable action timeline must not carry decisions")
    if timeline["status"] == "available" and not decisions:
        raise PublisherError("available action timeline needs at least one decision")

    evidence = manifest["evidence"]
    for field in ("video_url", "replay_url", "evidence_reference"):
        safe_public_url(evidence[field])
    availability = evidence["availability"]
    video = evidence["video_url"] is not None
    replay = evidence["replay_url"] is not None
    expected_media = {
        "none": (False, False),
        "report_only": (False, False),
        "video": (True, False),
        "replay_package": (False, True),
        "video_and_replay": (True, True),
    }[availability]
    if (video, replay) != expected_media:
        raise PublisherError(f"evidence URLs do not match availability={availability}")
    if availability == "report_only" and not evidence["evidence_reference"]:
        raise PublisherError("report-only evidence needs an evidence reference")
    if availability == "none" and evidence["evidence_reference"]:
        raise PublisherError("an unavailable evidence record may not expose an evidence reference")

    intervention = manifest["intervention"]
    if intervention["occurred"] and intervention["kind"] == "none":
        raise PublisherError("an occurred intervention needs a non-none kind")
    if not intervention["occurred"] and intervention["kind"] != "none":
        raise PublisherError("a non-none intervention kind must be marked occurred")

    measured_model_calls = manifest["model_configuration"]["calls_measured"]
    measured_budget_calls = manifest["resource_budget"]["provider_calls"]
    if measured_model_calls != measured_budget_calls:
        raise PublisherError("model and resource budget provider-call metadata do not match")

    card = manifest["decision_card"]
    if card["status"] == "unavailable":
        if any(card[field] is not None for field in ("asset_id", "artifact_digest", "provenance_reference")):
            raise PublisherError("unavailable decision card must not carry artifact fields")
        if card["provenance_status"] != "unverified":
            raise PublisherError("unavailable decision card cannot be approved")
    else:
        if not all(card[field] is not None for field in ("asset_id", "artifact_digest", "provenance_reference")):
            raise PublisherError("available decision card needs complete artifact lineage")
        if card["provenance_status"] != "approved":
            raise PublisherError("available decision card needs approved provenance")
        safe_public_url(card["provenance_reference"])

    case_study = manifest["case_study"]
    labels = {reference["label"] for reference in manifest["source"]["references"]}
    if case_study["status"] == "published":
        if not case_study["summary"] or case_study["source_reference"] not in labels:
            raise PublisherError("published case study must point to an included source reference")
    elif case_study["summary"] is not None or case_study["source_reference"] is not None:
        raise PublisherError("unavailable case study must not carry a summary or source reference")

    guess = manifest["local_guess_reveal"]
    if guess["status"] == "available" and guess["legal_option_count"] < 1:
        raise PublisherError("available local guess/reveal needs a legal option")
    if guess["status"] == "available" and timeline["status"] != "available":
        raise PublisherError("local guess/reveal needs an available action timeline")

    if guess["status"] == "unavailable" and guess["legal_option_count"] != 0:
        raise PublisherError("unavailable local guess must have zero legal options")
    if guess["status"] == "available" and guess["legal_option_count"] != len(decisions[0]["legal_choices"]):
        raise PublisherError("local guess option count must match the first decision")

    if manifest["classification"] == "synthetic" and not manifest["test_fixture"]:
        raise PublisherError("synthetic records must be explicitly marked test_fixture")
    if manifest["evidence_kind"] == "forced_fixture" and not manifest["test_fixture"]:
        raise PublisherError("forced fixtures must be explicitly marked test_fixture")
    if manifest["recorded_at"] is not None:
        _parse_datetime(manifest["recorded_at"], "recorded_at")


def validate_approval(approval: dict[str, Any]) -> dict[str, Any]:
    reject_forbidden_fields(approval)
    validate_approval_schema(approval)
    ids = [asset["asset_id"] for asset in approval["approved_assets"]]
    if len(ids) != len(set(ids)):
        raise ApprovalError("approval contains duplicate asset IDs")
    return approval


def _field_allowed(path: str, allowed_fields: Iterable[str]) -> bool:
    for allowed in allowed_fields:
        if allowed == "*" or allowed == path:
            return True
        if allowed.endswith(".*") and path.startswith(allowed[:-2] + "."):
            return True
        if path.startswith(allowed + "."):
            return True
    return False


def _field_scope_allowed(path: str, allowed_fields: Iterable[str]) -> bool:
    """Return true when an approval allows the complete top-level field.

    A nested allowlist such as ``source.references`` cannot authorize the
    complete source object rendered by the page.  Callers must use the exact
    top-level field or its ``.*`` scope, which avoids a projection/renderer
    mismatch that could otherwise produce a partial or unsafe page.
    """

    allowed = tuple(allowed_fields)
    return any(candidate in ("*", path, path + ".*") for candidate in allowed)


def project_approved_fields(manifest: dict[str, Any], allowed_fields: Iterable[str]) -> dict[str, Any]:
    """Return a recursively allowlisted public projection."""

    allowed = tuple(allowed_fields)

    def project(value: Any, prefix: str) -> Any:
        if isinstance(value, dict):
            result: dict[str, Any] = {}
            for key in sorted(value):
                path = f"{prefix}.{key}" if prefix else key
                if _field_allowed(path, allowed) or any(
                    candidate.startswith(path + ".") for candidate in allowed
                ):
                    result[key] = project(value[key], path)
            return result
        if isinstance(value, list):
            return [project(item, prefix) for item in value]
        return value

    return project(manifest, "")


def validate_production_publication(
    manifest: dict[str, Any],
    approval: dict[str, Any] | None,
    *,
    now: datetime | None = None,
    artifact_root: Path | str | None = None,
) -> dict[str, Any]:
    """Apply the fail-closed production gate and return its projection."""

    validate_manifest(manifest)
    if approval is None:
        raise ProductionGateError("production publication requires a separate digest-bound approval record")
    validate_approval(approval)
    if manifest["classification"] != "approved_public":
        raise ProductionGateError("only approved_public records may enter production output")
    if manifest["test_fixture"] or manifest["evidence_kind"] == "forced_fixture":
        raise ProductionGateError("synthetic or forced-fixture content cannot enter production output")
    if manifest["evidence_kind"] == "report_only" or manifest["evidence_context"]["capture_scope"] == "report_only":
        if manifest["action_timeline"]["status"] != "unavailable" or manifest["local_guess_reveal"]["status"] != "unavailable":
            raise ProductionGateError("report-only production records cannot expose action decisions or local guesses")
    if manifest["approval_reference"] != approval["approval_id"]:
        raise ApprovalError("manifest approval_reference does not identify the supplied approval")
    if approval["target"] != manifest["public_run_id"]:
        raise ApprovalError("approval target does not match public run ID")
    if approval["source_digest"] != manifest["source"]["content_digest"]:
        raise ApprovalError("approval source digest does not match the sanitized source")
    if approval["revoked"]:
        raise ApprovalError("approval is revoked")
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    approved_at = _parse_datetime(approval["approved_at"], "approved_at")
    if approved_at > current:
        raise ApprovalError("approval is dated in the future")
    if approval["expires_at"] is not None and _parse_datetime(approval["expires_at"], "expires_at") <= current:
        raise ApprovalError("approval has expired")
    if "run_manifest" not in approval["allowed_surfaces"] or "run_page" not in approval["allowed_surfaces"]:
        raise ApprovalError("approval must cover both run_manifest and run_page")
    missing = sorted(
        field for field in REQUIRED_APPROVAL_FIELDS if not _field_scope_allowed(field, approval["allowed_fields"])
    )
    missing.extend(field for field in ("source.references.label", "source.references.uri") if not _field_allowed(field, approval["allowed_fields"]))
    if missing:
        raise ApprovalError("approval does not allow required public fields: " + ", ".join(missing))
    if manifest["recorded_at"] is None:
        raise ProductionGateError("approved public records need a recorded timestamp")
    if manifest["evidence"]["rights_status"] != "approved":
        raise ProductionGateError("production evidence needs approved rights")
    if manifest["evidence"]["caption_support"] == "none":
        raise ProductionGateError("production captions need evidence support")
    if manifest["model_configuration"]["provider"].casefold() == "none" or manifest["model_configuration"]["identifier"].casefold() == "none":
        raise ProductionGateError("production records need an identified model configuration")
    if manifest["case_study"]["status"] == "published" and "case_study" not in approval["allowed_surfaces"]:
        raise ApprovalError("published case study is outside the approval surfaces")
    if manifest["action_timeline"]["status"] == "available" and "decision_timeline" not in approval["allowed_surfaces"]:
        raise ApprovalError("available action timeline is outside the approval surfaces")
    if manifest["evidence"]["availability"] != "none" and "evidence_panel" not in approval["allowed_surfaces"]:
        raise ApprovalError("available evidence is outside the approval surfaces")
    cards = [manifest["decision_card"]] + [
        decision["decision_card"] for decision in manifest["action_timeline"]["decisions"]
        if decision["decision_card"] is not None
    ]
    available_cards = [card for card in cards if card["status"] == "available"]
    if available_cards and artifact_root is None:
        raise ApprovalError("decision cards require an approved artifact root")
    if artifact_root is not None:
        inspect_artifact_root(Path(artifact_root))
    assets = {asset["asset_id"]: asset for asset in approval["approved_assets"]}
    verified_assets = set()
    for card in available_cards:
        asset = assets.get(card["asset_id"])
        if asset is None or asset["artifact_digest"] != card["artifact_digest"] or asset["provenance_reference"] != card["provenance_reference"]:
            raise ApprovalError("decision card artifact and provenance are not included in the approval")
        path = checked_path(Path(artifact_root), asset["artifact_path"], must_exist=True)
        if asset["asset_id"] not in verified_assets:
            verify_raster_asset(path, asset)
            verified_assets.add(asset["asset_id"])
    public_uris = {reference["uri"] for reference in manifest["source"]["references"]}
    public_uris.update(value for key, value in manifest["evidence"].items() if key in {"video_url", "replay_url", "evidence_reference"} and value)
    public_uris.update(card["provenance_reference"] for card in available_cards)
    public_uris.update(decision["evidence_ref"] for decision in manifest["action_timeline"]["decisions"] if decision["evidence_ref"])
    if not public_uris.issubset(set(approval["approved_public_uris"])):
        raise ApprovalError("public URI is outside the approved source register")
    for uri in approval["approved_public_uris"]:
        safe_public_url(uri)
    projection = project_approved_fields(manifest, approval["allowed_fields"])
    # Escaping does not remove a private URL from visible text. Apply the
    # same register to URL-bearing text in the actual public projection.
    require_approved_text_uris(projection, approval["approved_public_uris"])
    require_registered_approval(approval)
    return validate_public_projection(projection)


__all__ = [
    "validate_manifest",
    "validate_manifest_integrity",
    "validate_approval",
    "validate_production_publication",
    "project_approved_fields",
]
