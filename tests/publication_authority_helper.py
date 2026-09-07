"""Isolated trusted registry for synthetic unit tests; never edits real config."""
import hashlib
import json
import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from publisher.canonical import canonical_json


@contextmanager
def trusted_registry(*approvals):
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / 'registry.json'
        def enroll(*records):
            path.write_text(json.dumps({'schema_version': 'publication-authorities-v1', 'approvals': [
                {'approval_id': approval['approval_id'], 'authority_reference': approval['authority_reference'], 'approval_digest': hashlib.sha256(canonical_json(approval)).hexdigest()}
                for approval in records
            ]}), encoding='utf-8')
        enroll(*approvals)
        with patch('publisher.authority.REGISTRY_PATH', path):
            yield enroll
