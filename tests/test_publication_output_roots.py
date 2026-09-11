import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from publisher import OfflinePublisher, source_digest
from publisher.errors import PublisherError
from tests.test_publication import FIXTURE, approved_fixture
from tests.publication_authority_helper import trusted_registry


class PublicationOutputRootTests(unittest.TestCase):
    def test_approval_and_artifact_trees_must_be_disjoint_in_both_directions(self):
        manifest, approval = approved_fixture()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'source').mkdir()
            (root / 'approval').mkdir()
            manifest_path = root / 'source/manifest.json'
            approval_path = root / 'approval/approval.json'
            manifest_path.write_text(json.dumps(manifest))
            approval_path.write_text(json.dumps(approval))
            for output in (root, approval_path.parent, approval_path.parent / 'output'):
                with self.subTest(output=output), self.assertRaises(PublisherError):
                    OfflinePublisher().publish(manifest_path, approval_path, output)
            output = root / 'output'
            output.mkdir()
            (output / 'private.txt').write_text('unapproved')
            with self.assertRaises(PublisherError):
                OfflinePublisher().publish(manifest_path, approval_path, output, artifact_root=output)
            self.assertEqual((output / 'private.txt').read_text(), 'unapproved')

    def test_unregistered_content_and_sibling_symlinks_fail_without_removal(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            leak = output / 'private.txt'
            leak.write_text('unapproved')
            with self.assertRaises(PublisherError):
                OfflinePublisher().render(FIXTURE, output)
            self.assertEqual(leak.read_text(), 'unapproved')
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as source:
            output = Path(temp)
            target = Path(source) / 'private.txt'
            target.write_text('unapproved')
            (output / 'leak').symlink_to(target)
            with self.assertRaises(PublisherError):
                OfflinePublisher().render(FIXTURE, output)
            self.assertTrue((output / 'leak').is_symlink())

    def test_multiple_runs_remain_supported_but_foreign_files_are_not_adopted(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as source:
            output = Path(temp)
            first = OfflinePublisher().render(FIXTURE, output)
            manifest = json.loads(FIXTURE.read_text())
            manifest['public_run_id'] = 'second-synthetic-run'
            manifest['action_timeline']['public_run_id'] = manifest['public_run_id']
            for decision in manifest['action_timeline']['decisions']:
                decision['public_run_id'] = manifest['public_run_id']
            manifest['source']['content_digest'] = source_digest(manifest)
            path = Path(source) / 'manifest.json'
            path.write_text(json.dumps(manifest))
            second = OfflinePublisher().render(path, output)
            self.assertTrue(first.html_path.exists() and second.html_path.exists())
            self.assertTrue(OfflinePublisher().render(FIXTURE, output).idempotent)
            (output / 'private.txt').write_text('foreign')
            with self.assertRaises(PublisherError):
                OfflinePublisher().render(FIXTURE, output)
            self.assertEqual((output / 'private.txt').read_text(), 'foreign')

    def test_state_commit_failure_rolls_back_only_new_version_and_can_retry(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            with patch('publisher.output_state._save', side_effect=OSError('injected state failure')):
                with self.assertRaises(OSError):
                    OfflinePublisher().render(FIXTURE, output)
            self.assertEqual(list(output.iterdir()), [])
            result = OfflinePublisher().render(FIXTURE, output)
            self.assertTrue(result.html_path.exists())
