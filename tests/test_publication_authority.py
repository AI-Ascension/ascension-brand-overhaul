import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from publisher.errors import ApprovalError
from publisher.publisher import OfflinePublisher
from publisher.validate import REQUIRED_APPROVAL_FIELDS, validate_production_publication
from tests.publication_authority_helper import trusted_registry
from tests.test_publication import approved_fixture


class PublicationAuthorityTests(unittest.TestCase):
    def test_caller_supplied_authority_is_not_enough(self):
        manifest, approval = approved_fixture()
        with trusted_registry():
            with self.assertRaisesRegex(ApprovalError, 'not enrolled'):
                validate_production_publication(manifest, approval)
        with trusted_registry(approval):
            validate_production_publication(manifest, approval)
            approval['authority_reference'] = 'forged-authority'
            with self.assertRaisesRegex(ApprovalError, 'not enrolled'):
                validate_production_publication(manifest, approval)

    def test_enrolled_approval_rejects_changed_renderer_and_removed_uri(self):
        manifest, approval = approved_fixture()
        with trusted_registry(approval), patch('publisher.authority.renderer_digest', return_value='0' * 64):
            with self.assertRaisesRegex(ApprovalError, 'revision is stale'):
                validate_production_publication(manifest, approval)
        approval['approved_public_uris'] = []
        with trusted_registry(approval):
            with self.assertRaisesRegex(ApprovalError, 'URI is outside'):
                validate_production_publication(manifest, approval)

    def test_private_source_identity_can_be_withheld_from_json_and_html(self):
        manifest, approval = approved_fixture()
        approval['allowed_fields'] = sorted(REQUIRED_APPROVAL_FIELDS) + ['source.references.label', 'source.references.uri']
        with trusted_registry(approval), tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as output:
            source = Path(source)
            (source / 'manifest.json').write_text(json.dumps(manifest))
            (source / 'approval.json').write_text(json.dumps(approval))
            result = OfflinePublisher().publish(source / 'manifest.json', source / 'approval.json', output)
            projection = json.loads(result.manifest_path.read_text())
            self.assertEqual(set(projection['source']), {'references'})
            self.assertEqual(set(projection['source']['references'][0]), {'label', 'uri'})
            for path in (result.manifest_path, result.html_path):
                payload = path.read_text()
                self.assertNotIn(manifest['source']['content_digest'], payload)
                self.assertNotIn(manifest['source']['record_id'], payload)
                self.assertNotIn('Source content digest', payload)
