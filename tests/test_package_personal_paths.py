import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validate_package', ROOT / 'scripts/validate_package.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class PackagePersonalPathTests(unittest.TestCase):
    def test_every_workstation_path_form_is_reported_without_echoing_it(self):
        forms = {
            'linux-home.json': '{"path": "/home/someone/.cache/tool"}',
            'wsl-mount.json': '{"path": "/mnt/c/users/someone/documents/project"}',
            'windows-backslash.md': 'Checked out at C:\\Users\\Someone\\project',
            'windows-slash.txt': 'Checked out at c:/users/someone/project',
            'macos-home.py': 'ROOT = "/Users/someone/project"',
            'wsl-unc.md': 'Opened \\\\wsl.localhost\\Ubuntu\\home\\someone',
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, text in forms.items():
                (root / name).write_text(text, encoding='utf-8')
            errors = validator.personal_path_errors(root, exemptions=set())
            self.assertEqual(len(errors), len(forms), errors)
            for name in forms:
                self.assertTrue(any(f'Personal filesystem path in {name}: line(s) 1' == error for error in errors), errors)
            for error in errors:
                self.assertNotIn('someone', error.casefold())

    def test_neutral_placeholders_relative_paths_and_binaries_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'review.json').write_text('{"path": "<workstation>/sts2-project/sts2-project-worktrees/brand-root-art", "receipt": "execution/reviews/review.json", "profile": "https://example.test/users/someone"}', encoding='utf-8')
            (root / 'notes.md').write_text('The homepage lives at site/home/index.html and mirrors public/mnt/c/users/index.html', encoding='utf-8')
            (root / 'self-test.py').write_text('EXAMPLE = "/home/someone/pattern-source"', encoding='utf-8')
            (root / 'not-shipped.md').write_text('Package tests must not exempt this file', encoding='utf-8')
            self.assertEqual(validator.personal_path_errors(root, exemptions=set()), ['Personal filesystem path in self-test.py: line(s) 1'])
            (root / 'self-test.py').unlink()
            (root / 'capture.png').write_bytes(b'\x89PNG\r\n\x1a\n/home/someone/binary-noise')
            self.assertEqual(validator.personal_path_errors(root, exemptions=set()), [])

    def test_exemptions_only_cover_frozen_receipts_and_report_stale_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'frozen.json').write_text('{"path": "/home/someone/frozen"}', encoding='utf-8')
            (root / 'new.json').write_text('{"path": "/mnt/c/Users/someone/new"}', encoding='utf-8')
            errors = validator.personal_path_errors(root, exemptions={'frozen.json'})
            self.assertEqual(errors, ['Personal filesystem path in new.json: line(s) 1'])
            (root / 'new.json').write_text('{"path": "<workstation>/new"}', encoding='utf-8')
            (root / 'frozen.json').write_text('{"path": "<workstation>/frozen"}', encoding='utf-8')
            self.assertEqual(validator.personal_path_errors(root, exemptions={'frozen.json'}), ['Stale personal-path exemption (no longer matches, remove it): frozen.json'])

    def test_package_exemptions_name_only_frozen_receipts_still_carrying_paths(self):
        for relative in sorted(validator.PERSONAL_PATH_EXEMPTIONS):
            self.assertTrue((ROOT / relative).is_file(), relative)
        self.assertEqual([error for error in validator.personal_path_errors(ROOT) if 'Stale' in error], [])


if __name__ == '__main__':
    unittest.main()
