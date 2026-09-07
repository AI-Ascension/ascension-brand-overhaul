"""Date-bounded metrics from an operator-enrolled upstream event receipt."""
from __future__ import annotations

import calendar
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .canonical import canonical_json
from .authority import renderer_digest
from .errors import PublisherError
from .schema import unique_schema_object, validate_instance
from .security import reject_symlink_path

REGISTRY_PATH = Path(__file__).resolve().parents[1] / 'config/measurement-authorities.json'


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def measurement_semantics_digest(contract: dict) -> str:
    """Bind metric/privacy definitions and the installed evaluator/schema code."""
    return hashlib.sha256(canonical_json({'publisher_revision_digest': renderer_digest(), 'event_contract': contract})).hexdigest()


def event_stream_digest(events: list[dict]) -> str:
    """Caller must first validate IDs and reject conflicting retries."""
    return hashlib.sha256(canonical_json(sorted(events, key=lambda event: event['event_id']))).hexdigest()


def parse_time(value: str) -> datetime:
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (ValueError, TypeError) as exc:
        raise PublisherError('invalid measurement scope timestamp') from exc
    if result.tzinfo is None:
        raise PublisherError('measurement scope timestamps require timezone')
    return result.astimezone(timezone.utc)


def require_scope(events: list[dict], receipt: dict | None, *, contract: dict, now: datetime | None = None) -> dict:
    if receipt is None:
        raise PublisherError('production metrics require an enrolled upstream scope receipt')
    validate_instance(receipt, 'measurement-scope.schema.json')
    if receipt['measurement_semantics_digest'] != measurement_semantics_digest(contract):
        raise PublisherError('measurement receipt semantics revision is stale')
    if receipt['event_stream_digest'] != event_stream_digest(events):
        raise PublisherError('measurement receipt does not match the event stream')
    expected_content_digest = hashlib.sha256(canonical_json(sorted(receipt["eligible_public_content_ids"]))).hexdigest()
    if receipt["public_content_registry_digest"] != expected_content_digest:
        raise PublisherError("public content registry digest does not match eligible IDs")
    reject_symlink_path(REGISTRY_PATH)
    try:
        with REGISTRY_PATH.open('rb') as handle:
            raw = handle.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise PublisherError('measurement registry exceeds size limit')
        registry = json.loads(raw, object_pairs_hook=unique_schema_object)
    except (OSError, ValueError) as exc:
        raise PublisherError('trusted measurement registry is unavailable or invalid') from exc
    if not isinstance(registry, dict) or set(registry) != {'schema_version', 'receipts'} or registry['schema_version'] != 'measurement-authorities-v1' or not isinstance(registry['receipts'], list):
        raise PublisherError('invalid trusted measurement registry')
    ids = set()
    for entry in registry['receipts']:
        if not isinstance(entry, dict) or set(entry) != {'receipt_id', 'receipt_digest'} or not all(isinstance(value, str) for value in entry.values()):
            raise PublisherError('invalid trusted measurement registry entry')
        if entry['receipt_id'] in ids:
            raise PublisherError('duplicate trusted measurement receipt ID')
        ids.add(entry['receipt_id'])
    expected = {'receipt_id': receipt['receipt_id'], 'receipt_digest': hashlib.sha256(canonical_json(receipt)).hexdigest()}
    if expected not in registry['receipts']:
        raise PublisherError('measurement receipt is not enrolled in the trusted registry')
    week = parse_time(receipt['week_start'])
    month = parse_time(receipt['month_start'])
    through = parse_time(receipt['observed_through'])
    reviewed = parse_time(receipt['reviewed_at'])
    current = now or utc_now()
    if current.tzinfo is None:
        raise PublisherError('measurement evaluation clock requires timezone')
    current = current.astimezone(timezone.utc)
    if through > reviewed or reviewed > current:
        raise PublisherError('measurement cutoff or receipt review is dated in the future')
    if receipt['reporting_mode'] == 'current' and (current - reviewed > timedelta(days=1) or current - through > timedelta(days=2)):
        raise PublisherError('current measurement receipt is stale; use an explicitly reviewed historical receipt')
    if week.weekday() != 0 or any((week.hour, week.minute, week.second, week.microsecond)):
        raise PublisherError('weekly scope must start Monday at midnight UTC')
    if month.day != 1 or any((month.hour, month.minute, month.second, month.microsecond)):
        raise PublisherError('monthly scope must start on the first day at midnight UTC')
    if through < week or through < month:
        raise PublisherError('observation cutoff predates the requested scope')
    known = {event['event_id'] for event in events}
    exclusions = receipt['excluded_events']
    excluded_ids = [entry['event_id'] for entry in exclusions]
    if len(set(excluded_ids)) != len(excluded_ids) or not set(excluded_ids).issubset(known):
        raise PublisherError('scope exclusions contain duplicate or unknown event IDs')
    month_end = month + timedelta(days=calendar.monthrange(month.year, month.month)[1])
    return {'week_start': week, 'week_end': week + timedelta(days=7), 'month_start': month, 'month_end': month_end, 'observed_through': through, 'reviewed_at': reviewed, 'evaluated_at': current}
