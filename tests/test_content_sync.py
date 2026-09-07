import copy
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('sync_content', Path(__file__).resolve().parents[1] / 'scripts/sync_content.py')
content = importlib.util.module_from_spec(spec)
spec.loader.exec_module(content)


class ContentSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'canonical'
        self.consumer = self.root / 'consumer'
        self.repo.mkdir()
        self.consumer.mkdir()
        self.git('init', '-q')
        (self.repo / 'brand').mkdir()
        self.source = self.repo / 'brand/tokens.css'
        self.source.write_text(':root { --ink: #201c17; }\n')
        self.plan = self.commit_source()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', '-c', 'commit.gpgsign=false', *args]).decode().strip()

    def commit_source(self):
        self.git('add', '--', 'brand/tokens.css')
        self.git('commit', '-qm', 'test fixture')
        return {'schema_version': 'brand-content-sync-v1', 'source_revision': self.git('rev-parse', 'HEAD'),
                'files': [{'source': 'brand/tokens.css', 'destination': 'assets/brand/tokens.css',
                           'sha256': hashlib.sha256(self.source.read_bytes()).hexdigest()}]}

    def test_dry_run_does_not_write_and_apply_is_repeatable(self):
        content.sync(self.repo, self.consumer, self.plan)
        self.assertEqual(list(self.consumer.iterdir()), [])
        content.sync(self.repo, self.consumer, self.plan, True)
        receipt = (self.consumer / content.RECEIPT).read_bytes()
        again = content.sync(self.repo, self.consumer, self.plan, True)
        self.assertEqual(again['changed_files'], [])
        self.assertEqual((self.consumer / content.RECEIPT).read_bytes(), receipt)
        self.assertEqual((self.consumer / 'assets/brand/tokens.css').read_bytes(), self.source.read_bytes())

    def test_sync_reads_pinned_object_despite_dirty_source(self):
        original = self.source.read_bytes()
        self.source.write_text('uncommitted change')
        content.sync(self.repo, self.consumer, self.plan, True)
        self.assertEqual((self.consumer / 'assets/brand/tokens.css').read_bytes(), original)

    def test_consumer_edits_are_preserved_when_source_changes(self):
        content.sync(self.repo, self.consumer, self.plan, True)
        target = self.consumer / 'assets/brand/tokens.css'
        target.write_text('operator edit')
        self.source.write_text(':root { --ink: #17120d; }\n')
        updated = self.commit_source()
        with self.assertRaisesRegex(ValueError, 'unrelated edits'):
            content.sync(self.repo, self.consumer, updated, True)
        self.assertEqual(target.read_text(), 'operator edit')

    def test_clean_previous_copy_can_update(self):
        content.sync(self.repo, self.consumer, self.plan, True)
        self.source.write_text(':root { --ink: #17120d; }\n')
        updated = self.commit_source()
        content.sync(self.repo, self.consumer, updated, True)
        self.assertEqual((self.consumer / 'assets/brand/tokens.css').read_bytes(), self.source.read_bytes())

    def test_unsafe_paths_and_wrong_hash_fail_before_writes(self):
        for path in ['../private.css', '/absolute.css', '.git/config.css', 'assets\\private.css', 'assets/../private.css']:
            with self.subTest(path=path):
                plan = copy.deepcopy(self.plan)
                plan['files'][0]['destination'] = path
                with self.assertRaises(ValueError):
                    content.sync(self.repo, self.consumer, plan, True)
        plan = copy.deepcopy(self.plan)
        plan['files'][0]['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            content.sync(self.repo, self.consumer, plan, True)
        self.assertEqual(list(self.consumer.iterdir()), [])

    def test_symlink_and_noncanonical_source_rejected(self):
        (self.consumer / 'assets').symlink_to(self.repo, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            content.sync(self.repo, self.consumer, self.plan, True)
        plan = copy.deepcopy(self.plan)
        plan['files'][0]['source'] = 'private/secrets.json'
        with self.assertRaisesRegex(ValueError, 'canonical'):
            content.sync(self.repo, self.consumer, plan, True)
