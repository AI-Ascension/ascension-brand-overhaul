"""Synthetic operator enrollment fixture, isolated from deployment config."""
import hashlib
import json
import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from publisher.canonical import canonical_json
from publisher.measurement_scope import event_stream_digest


def scope_fixture(events):
    eligible = sorted({event['content_id'] for event in events})
    return {
        'schema_version': 'measurement-scope-v1', 'receipt_id': 'synthetic-scope-receipt',
        'authority_reference': 'Synthetic test server; no real observations',
        'event_stream_digest': event_stream_digest(events),
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
        with patch('publisher.measurement_scope.REGISTRY_PATH', path):
            yield
