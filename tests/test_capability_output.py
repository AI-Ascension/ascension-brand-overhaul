import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from publisher.authority import renderer_digest
from publisher.canonical import canonical_json
from publisher.capabilities import load_capability_registry
from publisher.capability_renderer import render_registry
from publisher.errors import PublisherError
from tests.publication_authority_helper import trusted_registry
from tests.test_measurement import CAPABILITY_FIXTURE


class CapabilityOutputTests(unittest.TestCase):
    def test_local_preview_is_labelled_and_cannot_overwrite_or_target_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'source').mkdir()
            source = root / 'source/registry.json'
            source.write_bytes(CAPABILITY_FIXTURE.read_bytes())
            with self.assertRaises(PublisherError):
                render_registry(source, root / 'source/output.html')
            output = root / 'output/page.html'
            render_registry(source, output)
            original = output.read_bytes()
            self.assertIn(b'Local preview only', original)
            with self.assertRaises(PublisherError):
                render_registry(source, output)
            self.assertEqual(output.read_bytes(), original)

    def test_symlink_and_failed_atomic_install_leave_source_untouched(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'source').mkdir()
            source = root / 'source/registry.json'
            original = CAPABILITY_FIXTURE.read_bytes()
            source.write_bytes(original)
            (root / 'alias').symlink_to(root / 'source', target_is_directory=True)
            with self.assertRaises(PublisherError):
                render_registry(source, root / 'alias/page.html')
            with patch('publisher.capability_renderer.os.link', side_effect=OSError('injected atomic install failure')):
                with self.assertRaises(OSError):
                    render_registry(source, root / 'out/page.html')
            self.assertEqual(list((root / 'out').iterdir()), [])
            self.assertEqual(source.read_bytes(), original)

    def test_public_output_requires_dated_review_and_enrolled_exact_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'source').mkdir()
            source = root / 'source/registry.json'
            records = json.loads(CAPABILITY_FIXTURE.read_text())
            for record in records:
                record.update(review_status='approved', last_reviewed_at='2026-09-06T00:00:00Z')
            source.write_text(json.dumps(records))
            records, metadata = load_capability_registry(source)
            approval = {'schema_version': 'capability-approval-v1', 'approval_id': 'capability-test-approval', 'authority_reference': 'Synthetic test only', 'approved_at': '2026-01-01T00:00:00Z', 'expires_at': None, 'source_digest': hashlib.sha256(canonical_json({'records': records, 'metadata': metadata})).hexdigest(), 'renderer_digest': renderer_digest(), 'approved_public_uris': sorted({record['source_url'] for record in records}), 'revoked': False, 'operation': 'publish_capabilities', 'content_classification': 'approved_public'}
            approval_path = root / 'source/approval.json'
            approval_path.write_text(json.dumps(approval))
            output = root / 'out/page.html'
            with trusted_registry(), self.assertRaises(PublisherError):
                render_registry(source, output, approval_path=approval_path)
            self.assertFalse(output.exists())
            with trusted_registry(approval):
                render_registry(source, output, approval_path=approval_path)
            self.assertNotIn('Local preview only', output.read_text())
            records[0]['review_status'] = 'unreviewed'
            source.write_text(json.dumps(records))
            approval['source_digest'] = hashlib.sha256(canonical_json({'records': records, 'metadata': metadata})).hexdigest()
            approval_path.write_text(json.dumps(approval))
            with trusted_registry(approval), self.assertRaises(PublisherError):
                render_registry(source, root / 'out/unreviewed.html', approval_path=approval_path)
