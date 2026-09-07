import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from publisher.authority import renderer_digest
from publisher.canonical import canonical_json
from publisher.capabilities import load_capability_registry
from publisher.capability_renderer import render_registry
from publisher.errors import PublisherError
from tests.capability_envelope_helper import capability_envelope
from tests.publication_authority_helper import trusted_registry
from tests.test_measurement import CAPABILITY_FIXTURE


class CapabilityProvenanceTests(unittest.TestCase):
    def test_envelope_requires_complete_typed_metadata(self):
        envelope = capability_envelope(json.loads(CAPABILITY_FIXTURE.read_text()))
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'records.json'
            for field in envelope:
                if field in {'schema_version', 'capabilities'}:
                    continue
                value = copy.deepcopy(envelope)
                del value[field]
                path.write_text(json.dumps(value))
                with self.subTest(missing=field), self.assertRaises(PublisherError):
                    load_capability_registry(path)
            for field, value in [('collected_at', 42), ('source_snapshot', []), ('baseline_package_revision', 'unknown'), ('review_boundary', {}), ('claim_policy', {})]:
                malformed = {**envelope, field: value}
                path.write_text(json.dumps(malformed))
                with self.subTest(field=field), self.assertRaises(PublisherError):
                    load_capability_registry(path)
            path.write_text(json.dumps(envelope))
            self.assertEqual(load_capability_registry(path)[1]['collected_at'], envelope['collected_at'])

    def test_registered_capability_approval_cannot_emit_unregistered_claim_urls(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'source').mkdir()
            source = root / 'source/registry.json'
            records = json.loads(CAPABILITY_FIXTURE.read_text())
            for record in records:
                record.update(review_status='approved', last_reviewed_at='2026-09-06T00:00:00Z')
            for index, uri in enumerate(['https://private.example/secret', 'mailto:private@example.invalid', 'data:text/plain,private']):
                records[0]['claim'] = 'Reviewed claim ' + uri
                source.write_text(json.dumps(capability_envelope(records)))
                validated, metadata = load_capability_registry(source)
                approval = {'schema_version': 'capability-approval-v1', 'approval_id': 'capability-test-approval', 'authority_reference': 'Synthetic test only', 'approved_at': '2026-01-01T00:00:00Z', 'expires_at': None, 'source_digest': hashlib.sha256(canonical_json({'records': validated, 'metadata': metadata})).hexdigest(), 'renderer_digest': renderer_digest(), 'approved_public_uris': sorted({record['source_url'] for record in validated}), 'revoked': False, 'operation': 'publish_capabilities', 'content_classification': 'approved_public'}
                approval_path = root / 'source/approval.json'
                approval_path.write_text(json.dumps(approval))
                output = root / f'output/{index}.html'
                with trusted_registry(approval), self.assertRaisesRegex(PublisherError, 'URL-like text'):
                    render_registry(source, output, approval_path=approval_path)
                self.assertFalse(output.exists())
