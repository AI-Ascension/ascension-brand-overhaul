import hashlib
import base64
import tempfile
import unittest
from pathlib import Path

from publisher.canonical import source_digest
from publisher.errors import PublisherError
from publisher.validate import validate_production_publication
from tests.test_publication import approved_fixture, load_fixture
from tests.publication_authority_helper import trusted_registry


PIXEL = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=')


class PublicationArtifactTests(unittest.TestCase):
    def fixture(self, nested=False):
        manifest, approval = approved_fixture()
        card = {'status': 'available', 'asset_id': 'decision-art', 'artifact_digest': hashlib.sha256(PIXEL).hexdigest(), 'provenance_reference': '/press/provenance/decision-art.json', 'provenance_status': 'approved'}
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
        approval['approved_assets'] = [{'asset_id': card['asset_id'], 'artifact_digest': card['artifact_digest'], 'artifact_path': 'card.png', 'mime_type': 'image/png', 'byte_size': len(PIXEL), 'provenance_reference': card['provenance_reference']}]
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
                (root / 'card.png').write_bytes(PIXEL)
                validate_production_publication(manifest, approval, artifact_root=root)
                approval['approved_assets'] = []
                with self.assertRaises(PublisherError):
                    validate_production_publication(manifest, approval, artifact_root=root)

    def test_mime_extension_size_metadata_and_trailing_payload_fail(self):
        from publisher.artifacts import verify_raster_asset
        import struct
        import zlib
        manifest, approval = self.fixture()
        asset = approval['approved_assets'][0]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / 'card.bin'
            path.write_bytes(PIXEL)
            with self.assertRaises(PublisherError):
                verify_raster_asset(path, asset)
            path = root / 'card.jpg'
            path.write_bytes(PIXEL)
            with self.assertRaises(PublisherError):
                verify_raster_asset(path, dict(asset, mime_type='image/jpeg'))
            path = root / 'card.png'
            path.write_bytes(PIXEL)
            with self.assertRaises(PublisherError):
                verify_raster_asset(path, dict(asset, byte_size=len(PIXEL)+1))
            text = b'tEXt' + b'Comment\x00private test metadata'
            chunk = struct.pack('>I', len(text)-4) + text + struct.pack('>I', zlib.crc32(text))
            for raw in (PIXEL + b'private trailing test data', PIXEL[:33] + chunk + PIXEL[33:]):
                path.write_bytes(raw)
                changed = dict(asset, byte_size=len(raw), artifact_digest=hashlib.sha256(raw).hexdigest())
                with self.assertRaises(PublisherError):
                    verify_raster_asset(path, changed)

    def test_artifact_scan_has_per_file_aggregate_and_entry_limits(self):
        from publisher.security import inspect_artifact_root
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with (root / 'oversized.bin').open('wb') as handle:
                handle.truncate(16*1024*1024+1)
            with self.assertRaises(PublisherError):
                inspect_artifact_root(root)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for index in range(5):
                with (root / str(index)).open('wb') as handle:
                    handle.truncate(16*1024*1024)
            with self.assertRaises(PublisherError):
                inspect_artifact_root(root)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for index in range(1025):
                (root / str(index)).touch()
            with self.assertRaises(PublisherError):
                inspect_artifact_root(root)
