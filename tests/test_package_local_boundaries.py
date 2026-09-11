import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validate_package', ROOT / 'scripts/validate_package.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class PackageLocalBoundaryTests(unittest.TestCase):
    def test_local_dependencies_do_not_enter_source_validation_but_owned_fonts_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / 'brief'
            shutil.copytree(ROOT, fixture, ignore=shutil.ignore_patterns(*validator.LOCAL_ONLY_DIRECTORIES))
            for name in ['node_modules', '.execution-private']:
                local = fixture / name
                local.mkdir()
                (local / 'incomplete.json').write_text('not a source file')
                (local / 'local-font.woff2').write_bytes(b'local dependency')
                (local / 'link').symlink_to(fixture / 'README.md')
            self.assertEqual(validator.validate(fixture), [])
            (fixture / 'unapproved-font.woff2').write_bytes(b'not allowed in delivery')
            self.assertTrue(any('Font binary found' in error for error in validator.validate(fixture)))
