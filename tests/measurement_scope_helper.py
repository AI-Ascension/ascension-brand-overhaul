"""Synthetic operator enrollment fixture, isolated from deployment config."""
import hashlib
import json
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from publisher.canonical import canonical_json
from publisher.measurement_scope import event_stream_digest, measurement_semantics_digest
from publisher.events import load_event_contract


def scope_fixture(events):
    eligible = sorted({event['content_id'] for event in events})
    return {
        'schema_version': 'measurement-scope-v1', 'receipt_id': 'synthetic-scope-receipt',
        'authority_reference': 'Synthetic test server; no real observations',
        'event_stream_digest': event_stream_digest(events),
        'measurement_semantics_digest': measurement_semantics_digest(load_event_contract()),
        'reporting_mode': 'current',
        'reviewed_at': '2026-09-08T00:00:00Z',
        'week_start': '2026-09-07T00:00:00Z', 'month_start': '2026-09-01T00:00:00Z',
        'observed_through': '2026-09-08T00:00:00Z',
        'public_content_registry_reference': 'synthetic-public-registry',
        'public_content_registry_digest': hashlib.sha256(canonical_json(eligible)).hexdigest(),
        'eligible_public_content_ids': eligible,
        'server_rules_reference': 'synthetic-server-rules', 'excluded_events': [],
    }


@contextmanager
def trusted_scope(receipt):
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / 'registry.json'
        path.write_text(json.dumps({'schema_version': 'measurement-authorities-v1', 'receipts': [
            {'receipt_id': receipt['receipt_id'], 'receipt_digest': hashlib.sha256(canonical_json(receipt)).hexdigest()}
        ]}))
        with patch('publisher.measurement_scope.REGISTRY_PATH', path), patch('publisher.measurement_scope.utc_now', return_value=datetime(2026, 9, 8, tzinfo=timezone.utc)):
            yield
