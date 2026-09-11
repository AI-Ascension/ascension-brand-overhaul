import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('sync_content', Path(__file__).resolve().parents[1] / 'scripts/sync_content.py')
content = importlib.util.module_from_spec(spec)
spec.loader.exec_module(content)


class ContentSyncTests(unittest.TestCase):
    def test_forged_receipt_cannot_authorize_consumer_edit(self):
        content.sync(self.repo, self.consumer, self.plan, True)
        target = self.consumer / 'assets/brand/tokens.css'
        target.write_text('operator edit')
        receipt_path = self.consumer / content.RECEIPT
        receipt = json.loads(receipt_path.read_text())
        receipt['files'][0]['sha256'] = content.digest(target.read_bytes())
        receipt_path.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ValueError, 'protected canonical authority'):
            content.sync(self.repo, self.consumer, self.plan, True)
        self.assertEqual(target.read_text(), 'operator edit')

    def test_deleted_managed_copy_is_preserved(self):
        content.sync(self.repo, self.consumer, self.plan, True)
        target = self.consumer / 'assets/brand/tokens.css'
        target.unlink()
        with self.assertRaisesRegex(ValueError, 'unrelated edits'):
            content.sync(self.repo, self.consumer, self.plan, True)
        self.assertFalse(target.exists())

    def test_cooperative_lock_blocks_apply_and_dry_run(self):
        with content.consumer_lock(self.consumer):
            for apply in (False, True):
                with self.assertRaisesRegex(ValueError, 'locked'):
                    content.sync(self.repo, self.consumer, self.plan, apply)
        self.assertEqual(list(self.consumer.iterdir()), [])

    def test_multifile_failure_restores_content_receipt_and_authority(self):
        copy_path = self.repo / 'brand/copy.json'
        copy_path.write_text('{"title":"Before"}')
        self.git('add', '--', 'brand/copy.json')
        initial = self.commit_source()
        initial['files'].append({'source': 'brand/copy.json', 'destination': 'assets/brand/copy.json', 'sha256': content.digest(copy_path.read_bytes())})
        content.sync(self.repo, self.consumer, initial, True)
        self.source.write_text(':root { --ink: #17120d; }\n')
        copy_path.write_text('{"title":"After"}')
        self.git('add', '--', 'brand/copy.json')
        updated = self.commit_source()
        updated['files'].append({'source': 'brand/copy.json', 'destination': 'assets/brand/copy.json', 'sha256': content.digest(copy_path.read_bytes())})
        state = self.repo / '.git/ai-ascension-content-sync'
        before = {p: p.read_bytes() for base in (self.consumer, state) for p in base.rglob('*') if p.is_file()}
        real_write = content.atomic_write
        for fail_at in (2, 3, 4):
            for after_replace in (False, True):
                with self.subTest(fail_at=fail_at, after_replace=after_replace):
                    calls = 0
                    def fail_once(path, raw):
                        nonlocal calls
                        calls += 1
                        if calls == fail_at and not after_replace:
                            raise OSError('injected write failure')
                        real_write(path, raw)
                        if calls == fail_at:
                            raise OSError('injected post-replace failure')
                    with patch.object(content, 'atomic_write', fail_once):
                        with self.assertRaises(OSError):
                            content.sync(self.repo, self.consumer, updated, True)
                    self.assertEqual({p: p.read_bytes() for base in (self.consumer, state) for p in base.rglob('*') if p.is_file()}, before)
        content.sync(self.repo, self.consumer, updated, True)
        self.assertEqual((self.consumer / 'assets/brand/copy.json').read_bytes(), copy_path.read_bytes())

    def test_concurrent_edit_keeps_lock_and_recovery_journal(self):
        real_write = content.atomic_write
        target = self.consumer / 'assets/brand/tokens.css'
        def interfere(path, raw):
            real_write(path, raw)
            path.write_text('concurrent operator edit')
            raise OSError('injected interruption')
        with patch.object(content, 'atomic_write', interfere):
            with self.assertRaisesRegex(ValueError, 'Rollback is incomplete'):
                content.sync(self.repo, self.consumer, self.plan, True)
        self.assertEqual(target.read_text(), 'concurrent operator edit')
        self.assertTrue((self.consumer / content.LOCK_NAME).exists())
        self.assertEqual(len(list((self.repo / '.git/ai-ascension-content-sync').glob('*.transaction-*/journal.json'))), 1)

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
