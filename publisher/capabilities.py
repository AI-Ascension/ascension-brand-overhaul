"""Current-capability validation and deterministic rendering."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Iterable

from .schema import unique_schema_object, validate_capability_schema
from .security import reject_forbidden_fields, reject_symlink_path, safe_public_url


W01_REGISTRY_SCHEMA = "ai-ascension.capabilities.v1"
W01_REGISTRY_FIELDS = {
    "schema_version",
    "collected_at",
    "source_snapshot",
    "baseline_package_revision",
    "review_boundary",
    "capabilities",
    "claim_policy",
}
W01_REVIEW_FIELDS = {
    "collector_role", "collector_thread_id", "independent_reviewer",
    "independent_review_status", "interpretation",
}
W01_CLAIM_POLICY_FIELDS = {
    "verified_win", "current_public_video", "current_public_replay_package",
    "live_autonomous_service", "native_multiplayer", "trademark_clearance",
    "unsupported_claims_to_avoid",
}


def load_capability_registry(path: str | Path) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """Load a capability array or the W01 registry envelope without renaming IDs.

    W01 owns ``execution/capabilities.json`` and may add current source
    records there.  This adapter accepts the observed envelope shape and
    returns its records unchanged (apart from deterministic ordering for
    rendering).  It intentionally does not invent source facts when the
    registry is absent.
    """

    raw_path = Path(path)
    reject_symlink_path(raw_path)
    if raw_path.is_symlink():
        raise ValueError(f"capability registry must be a real JSON file: {path}")
    path = raw_path.resolve()
    if not path.is_file():
        raise ValueError(f"capability registry must be a real JSON file: {path}")
    with path.open("rb") as handle:
        raw = handle.read(4 * 1024 * 1024 + 1)
    if len(raw) > 4 * 1024 * 1024:
        raise ValueError("capability registry exceeds the 4 MiB limit")
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_schema_object)
    reject_forbidden_fields(value)
    metadata: dict[str, Any] | None = None
    if isinstance(value, list):
        records = value
    elif isinstance(value, dict) and value.get("schema_version") == W01_REGISTRY_SCHEMA:
        unknown = sorted(set(value) - W01_REGISTRY_FIELDS)
        if unknown:
            raise ValueError("unknown W01 capability registry fields: " + ", ".join(unknown))
        for nested_name, nested_fields in (
            ("review_boundary", W01_REVIEW_FIELDS),
            ("claim_policy", W01_CLAIM_POLICY_FIELDS),
        ):
            nested = value.get(nested_name)
            if nested is not None:
                if not isinstance(nested, dict):
                    raise ValueError(f"W01 {nested_name} must be an object")
                nested_unknown = sorted(set(nested) - nested_fields)
                if nested_unknown:
                    raise ValueError(
                        f"unknown W01 {nested_name} fields: " + ", ".join(nested_unknown)
                    )
        records = value.get("capabilities")
        metadata = {
            key: value[key]
            for key in (
                "schema_version", "collected_at", "source_snapshot", "baseline_package_revision",
                "review_boundary", "claim_policy",
            )
            if key in value
        }
    else:
        raise ValueError("capability registry must be an array or the W01 ai-ascension.capabilities.v1 envelope")
    if not isinstance(records, list):
        raise ValueError("capability registry capabilities must be an array")
    # Preserve exact source IDs and fields; validation is the only semantic
    # transformation.  The renderer sorts a copy by capability_id.
    return validate_capabilities(records), metadata


def validate_capability(record: dict[str, Any]) -> dict[str, Any]:
    reject_forbidden_fields(record)
    return validate_capability_schema(record)


def validate_capabilities(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    validated = [validate_capability(record) for record in records]
    ids = [record["capability_id"] for record in validated]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate capability_id")
    return sorted(validated, key=lambda record: record["capability_id"])


def render_capabilities(records: Iterable[dict[str, Any]]) -> str:
    """Render capability states without turning absent observations into zero."""

    rows = []
    for record in validate_capabilities(records):
        esc = lambda value: html.escape(str(value), quote=True)
        observed = record.get("observed_at") or "No observation date"
        safe_public_url(record["source_url"])
        rows.append(
            "<tr>"
            f"<th scope=\"row\">{esc(record['display_label'])}</th>"
            f"<td>{esc(record['claim'])}<br><a href=\"{esc(record['source_url'])}\" rel=\"noreferrer\">Source</a> · {esc(record['source_revision'])}</td>"
            f"<td>{esc(record['evidence_kind'])}</td>"
            f"<td>{esc(record['verification_actor'])}</td>"
            f"<td>{esc(record['public_artifact_availability'])}</td>"
            f"<td>{esc(record['release_support'])}</td>"
            f"<td>{esc(record['review_status'])} · {esc(observed)}</td>"
            "</tr>"
        )
    body = "".join(rows) or "<tr><td colspan=\"7\">No capability records.</td></tr>"
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><title>Capabilities · AI Ascension</title>"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"></head><body>"
        "<main><h1>Current capabilities</h1>"
        "<p>Evidence type, verification actor, public artifact availability, and release support are separate fields.</p>"
        "<p>No analytics observations are included in this capability render.</p>"
        "<table><thead><tr><th>Capability</th><th>Claim</th><th>Evidence</th><th>Verification</th>"
        "<th>Public artifact</th><th>Release support</th><th>Review</th></tr></thead>"
        f"<tbody>{body}</tbody></table></main></body></html>\n"
    )


__all__ = ["load_capability_registry", "validate_capability", "validate_capabilities", "render_capabilities"]
