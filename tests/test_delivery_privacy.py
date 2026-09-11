import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('build_delivery', Path(__file__).resolve().parents[1] / 'scripts/build_delivery.py')
archive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)


class DeliveryPrivacyTests(unittest.TestCase):
    def test_runtime_approvals_and_native_logs_never_enter_delivery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'
            source.mkdir()
            (source / 'public.md').write_text('approved text')
            for name in ['.execution-private', '.EXECUTION-PRIVATE', '.codex', '.agents']:
                private = source / name
                private.mkdir()
                (private / 'approvals.json').write_text('{"private":"not for delivery"}')
            archive.build(source, root / 'delivery.zip')
            with zipfile.ZipFile(root / 'delivery.zip') as result:
                self.assertEqual(result.namelist(), ['source/public.md'])

    def test_existing_delivery_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'
            source.mkdir()
            destination = root / 'delivery.zip'
            destination.write_bytes(b'existing operator artifact')
            with self.assertRaises(FileExistsError):
                archive.build(source, destination)
            self.assertEqual(destination.read_bytes(), b'existing operator artifact')
