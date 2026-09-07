"""Validation and aggregation for privacy-minimal engagement events."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .errors import PublisherError
from .schema import validate_event_contract_schema, validate_event_schema
from .security import reject_forbidden_fields


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "analytics" / "event-contract.json"


def load_event_contract() -> dict[str, Any]:
    try:
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PublisherError(f"cannot read event contract: {exc}") from exc
    if not isinstance(contract, dict):
        raise PublisherError("event contract must be an object")
    validate_event_contract_schema(contract)
    _validate_contract_definitions(contract)
    return contract


def _event_definition(name: str, contract: dict[str, Any]) -> dict[str, Any]:
    for definition in contract["events"]:
        if definition["name"] == name:
            return definition
    raise PublisherError(f"unknown event name: {name}")


def _validate_contract_definitions(contract: dict[str, Any]) -> None:
    """Check semantic constraints that JSON Schema does not express."""

    definitions = contract["events"]
    names = [definition["name"] for definition in definitions]
    if len(names) != len(set(names)):
        raise PublisherError("event contract contains duplicate event names")
    for definition in definitions:
        if not set(definition["required_properties"]).issubset(definition["allowed_properties"]):
            raise PublisherError(
                f"{definition['name']} required properties must be allowed properties"
            )


def _parse_event_time(event: dict[str, Any]) -> datetime:
    try:
        parsed = datetime.fromisoformat(event["occurred_at"].replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise PublisherError("event occurred_at must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise PublisherError("event occurred_at must include a timezone")
    parsed = parsed.astimezone(timezone.utc)
    if event["timestamp_precision"] == "day" and (parsed.hour or parsed.minute or parsed.second or parsed.microsecond):
        raise PublisherError("day precision event timestamps must be midnight")
    if event["timestamp_precision"] == "minute" and (parsed.second or parsed.microsecond):
        raise PublisherError("minute precision event timestamps must have zero seconds")
    return parsed


def validate_event(event: dict[str, Any], *, contract: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate schema, event-specific fields, consent, and server observations."""

    reject_forbidden_fields(event)
    validate_event_schema(event)
    contract = contract or load_event_contract()
    definition = _event_definition(event["event_name"], contract)
    if event["surface"] != definition["surface"]:
        raise PublisherError(f"{event['event_name']} must use surface={definition['surface']}")
    _parse_event_time(event)
    properties = event["properties"]
    required = set(definition["required_properties"])
    allowed = set(definition["allowed_properties"])
    missing = sorted(required - set(properties))
    extra = sorted(set(properties) - allowed)
    if missing:
        raise PublisherError(f"{event['event_name']} is missing properties: {', '.join(missing)}")
    if extra:
        raise PublisherError(f"{event['event_name']} has disallowed properties: {', '.join(extra)}")
    if definition["consent_required"] and event["consent_state"] != "granted":
        raise PublisherError(f"{event['event_name']} requires granted consent")
    if definition["server_confirmed"] and event["server_observation"] != "confirmed":
        raise PublisherError(f"{event['event_name']} requires a server-confirmed observation")
    if event["event_name"] in {"quickstart_success", "subscribe_confirmed", "unsubscribe_completed"} and properties.get("status") != "completed":
        raise PublisherError("completion events require status=completed")
    cohort = event["coarse_cohort"]
    if cohort and cohort["value"] is not None and event["consent_state"] != "granted":
        raise PublisherError("a valued coarse cohort requires granted consent")
    if cohort and cohort["kind"] == "consented_cohort":
        if event["consent_state"] != "granted":
            raise PublisherError("a consented coarse cohort requires granted consent")
        if cohort["value"] is None:
            raise PublisherError("a consented coarse cohort requires a bucket value")
    return event


def validate_events(events: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    contract = load_event_contract()
    result: list[dict[str, Any]] = []
    for event in events:
        result.append(validate_event(event, contract=contract))
    return result


def aggregate_events(
    events: Iterable[dict[str, Any]],
    *,
    include_synthetic: bool = False,
) -> dict[str, Any]:
    """Compute documented metrics, using ``None`` for absent observations."""

    contract = load_event_contract()
    validated = [validate_event(event, contract=contract) for event in events]
    # De-duplicate by server-issued event ID before calculating any rate.  A
    # retry or replayed request must not inflate an audience denominator.
    unique: list[dict[str, Any]] = []
    seen_ids: dict[str, str] = {}
    for event in validated:
        canonical = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        if event["event_id"] in seen_ids:
            if seen_ids[event["event_id"]] != canonical:
                raise PublisherError("conflicting duplicate event ID")
            continue
        seen_ids[event["event_id"]] = canonical
        unique.append(event)
    validated = unique if include_synthetic else [event for event in unique if event["environment"] == "production"]
    counts = Counter(event["event_name"] for event in validated)

    def ratio(numerator: int, denominator: int) -> float | None:
        return None if denominator == 0 else numerator / denominator

    values = {
        "audience-engagement-rate": ratio(counts["meaningful_watch_or_read"], counts["run_page_view"]),
        "decision-interaction-rate": ratio(
            counts["decision_guess"] + counts["decision_reveal"], counts["decision_presented"]
        ),
        "evidence-inspection-rate": ratio(counts["evidence_open"], counts["run_page_view"]),
        "developer-activation-rate": ratio(counts["quickstart_success"], counts["build_start"]),
        "repeat-engagement-proxy": (
            len(cohort_values)
            if (cohort_values := {
                event["coarse_cohort"]["value"]
                for event in validated
                if event["coarse_cohort"] and event["coarse_cohort"]["kind"] == "consented_cohort"
            })
            else None
        ),
        "publication-failure-count": (
            None
            if not validated
            else sum(
                event["properties"].get("status") == "failed"
                for event in validated
                if event["event_name"] in {"docs_error", "quickstart_success"}
            )
        ),
    }
    return {
        "schema_version": "measurement-result-v1",
        "environment": "synthetic" if include_synthetic else "production",
        "event_count": len(validated) if validated else None,
        "metrics": {
            metric_id: {"value": value, "state": "no_observations" if value is None else "observed"}
            for metric_id, value in values.items()
        },
    }


__all__ = ["load_event_contract", "validate_event", "validate_events", "aggregate_events"]
