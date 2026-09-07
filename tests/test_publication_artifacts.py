import hashlib
import tempfile
import unittest
from pathlib import Path

from publisher.canonical import source_digest
from publisher.errors import PublisherError
from publisher.validate import validate_production_publication
from tests.test_publication import approved_fixture, load_fixture
from tests.publication_authority_helper import trusted_registry


class PublicationArtifactTests(unittest.TestCase):
    def fixture(self, nested=False):
        manifest, approval = approved_fixture()
        card = {'status': 'available', 'asset_id': 'decision-art', 'artifact_digest': hashlib.sha256(b'approved-image').hexdigest(), 'provenance_reference': '/press/provenance/decision-art.json', 'provenance_status': 'approved'}
        if nested:
            manifest['evidence_kind'] = 'native_run'
            manifest['evidence_context']['capture_scope'] = 'state_only'
            manifest['action_timeline'] = load_fixture()['action_timeline']
            manifest['action_timeline']['decisions'][0]['decision_card'] = dict(card)
            manifest['action_timeline']['decisions'][0]['decision_card'].pop('provenance_status')
        else:
            manifest['decision_card'] = card
        manifest['source']['content_digest'] = source_digest(manifest)
        approval['source_digest'] = manifest['source']['content_digest']
        approval['approved_assets'] = [{'asset_id': card['asset_id'], 'artifact_digest': card['artifact_digest'], 'artifact_path': 'card.png', 'provenance_reference': card['provenance_reference']}]
        approval["approved_public_uris"].append(card["provenance_reference"])
        return manifest, approval

    def test_top_level_and_nested_cards_require_real_matching_approved_files(self):
        for nested in (False, True):
            manifest, approval = self.fixture(nested)
            with self.subTest(nested=nested), trusted_registry(approval), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                with self.assertRaises(PublisherError):
                    validate_production_publication(manifest, approval)
                with self.assertRaises(PublisherError):
                    validate_production_publication(manifest, approval, artifact_root=root)
                (root / 'card.png').write_bytes(b'wrong-image')
                with self.assertRaises(PublisherError):
                    validate_production_publication(manifest, approval, artifact_root=root)
                (root / 'card.png').write_bytes(b'approved-image')
                validate_production_publication(manifest, approval, artifact_root=root)
                approval['approved_assets'] = []
                with self.assertRaises(PublisherError):
                    validate_production_publication(manifest, approval, artifact_root=root)
