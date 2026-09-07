import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_delivery import build
from package_inventory import manifest_errors
from update_manifest import refresh


class PackageInventoryTests(unittest.TestCase):
    def fixture(self, root):
        root.mkdir()
        (root / 'public.md').write_text('Reviewed synthetic source\n')
        (root / 'MANIFEST.json').write_text(json.dumps({'package': 'Synthetic package', 'version': '1', 'integrity_exclusions': ['MANIFEST.json', 'CHECKSUMS.sha256'], 'files': []}))
        refresh(root, True)

    def test_unlisted_duplicate_and_unknown_manifest_entries_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'source'
            self.fixture(root)
            self.assertEqual(manifest_errors(root), [])
            (root / 'unlisted.json').write_text('{}')
            self.assertTrue(any('Unlisted package file' in error for error in manifest_errors(root)))
            (root / 'unlisted.json').unlink()
            manifest = json.loads((root / 'MANIFEST.json').read_text())
            manifest['files'].append(manifest['files'][0])
            (root / 'MANIFEST.json').write_text(json.dumps(manifest))
            self.assertTrue(any('Duplicate' in error for error in manifest_errors(root)))
            manifest['files'].pop()
            manifest['caller_override'] = True
            (root / 'MANIFEST.json').write_text(json.dumps(manifest))
            self.assertTrue(any('Invalid package manifest fields' in error for error in manifest_errors(root)))

    def test_case_insensitive_secret_exclusions_and_review_digest_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            root = parent / 'source'
            self.fixture(root)
            for name in ['.ENV', '.npmrc', 'credentials.json', 'AUTH.JSON', 'private.KEY', 'ID_ED25519']:
                (root / name).write_text('synthetic-secret')
            manifest_digest = hashlib.sha256((root / 'MANIFEST.json').read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, 'Reviewed manifest digest'):
                build(root, parent / 'wrong.zip', '0' * 64)
            self.assertFalse((parent / 'wrong.zip').exists())
            result = build(root, parent / 'reviewed.zip', manifest_digest)
            self.assertEqual(result['classification'], 'reviewed_source_archive')
            with zipfile.ZipFile(parent / 'reviewed.zip') as archive:
                self.assertEqual(set(archive.namelist()), {'source/public.md', 'source/MANIFEST.json', 'source/CHECKSUMS.sha256'})
                self.assertFalse(any(b'synthetic-secret' in archive.read(name) for name in archive.namelist()))

    def test_duplicate_json_members_do_not_silently_replace_control_values(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'source'
            self.fixture(root)
            raw = (root / 'MANIFEST.json').read_text().replace('"version": "1"', '"version": "0", "version": "1"')
            (root / 'MANIFEST.json').write_text(raw)
            self.assertTrue(any('Duplicate JSON object key' in error for error in manifest_errors(root)))
