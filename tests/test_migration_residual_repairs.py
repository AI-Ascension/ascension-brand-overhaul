import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tests.test_migration_review_repairs import MultiFakeClient, apply_plan_fixture
from tests.test_migration_tooling import FakeClient, migration, operation, repository


class MigrationResidualTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        home = patch.object(migration.Path, 'home', return_value=self.root)
        home.start()
        self.addCleanup(home.stop)

    def test_definite_failure_receipt_reloads_and_rechecks_before_retry(self):
        client = MultiFakeClient({'source': repository()}, rename_error=migration.ApiError('HTTP 422 Unprocessable Entity'))
        plan, path, receipt, approval = apply_plan_fixture(self.root, [operation()])
        first = migration.apply_plan(plan, client, plan_path=path, receipt_path=receipt, approval=approval, apply=True)
        self.assertEqual(first['operations'][0]['status'], 'failed')
        client.rename_error = None
        client.states['source']['head_sha'] = 'b' * 40
        second = migration.apply_plan(plan, client, plan_path=path, receipt_path=receipt, approval=approval, apply=True)
        self.assertEqual(second['operations'][0]['status'], 'blocked')
        self.assertEqual(len(client.rename_calls), 1)
        client.states['source']['head_sha'] = repository()['head_sha']
        third = migration.apply_plan(plan, client, plan_path=path, receipt_path=receipt, approval=approval, apply=True)
        self.assertEqual(third['operations'][0]['status'], 'applied')
        self.assertEqual(len(client.rename_calls), 2)

    def test_copied_plan_in_other_directory_uses_same_operation_lock(self):
        plan, path, receipt, approval = apply_plan_fixture(self.root, [operation()])
        copied = self.root / 'other/copied.json'
        copied.parent.mkdir()
        copied.write_bytes(path.read_bytes())
        digest = migration.sha256_bytes(path.read_bytes())
        lock = migration.operation_set_lock_path(path, digest)
        self.assertEqual(lock, migration.operation_set_lock_path(copied, digest))
        lock.parent.mkdir(parents=True)
        lock.write_text('active operation')
        client = FakeClient(repository())
        with self.assertRaisesRegex(migration.MigrationError, 'Operation set is locked'):
            migration.apply_plan(plan, client, plan_path=copied, receipt_path=self.root/'other/receipt.json', approval=approval, apply=True)
        self.assertEqual(client.rename_calls, [])

    def snapshot(self):
        return {'schema_version': 'fixture.v1', 'repositories': [{'full_name': 'AI-Ascension/source', 'stable_id': 10, 'default_branch': 'main', 'default_head': 'a'*40, 'visibility': 'public'}]}

    def test_map_cannot_override_any_snapshot_identity_precondition(self):
        for field, value in [('source_head', 'b'*40), ('default_branch', 'develop'), ('visibility', 'private')]:
            with self.subTest(field=field):
                row = {'source_name': 'source', 'target_name': 'target', 'action': 'rename', field: value}
                with self.assertRaisesRegex(migration.MigrationError, 'disagrees'):
                    migration.build_plan([row], FakeClient(repository()), snapshot=self.snapshot())

    def test_snapshot_digest_is_computed_from_matching_exact_bytes(self):
        snapshot = self.snapshot()
        row = {'source_name': 'source', 'target_name': 'target', 'action': 'rename'}
        with self.assertRaisesRegex(migration.MigrationError, 'digest disagrees'):
            migration.build_plan([row], FakeClient(repository()), snapshot=snapshot, snapshot_sha256='0'*64)
        raw = json.dumps(snapshot, indent=4).encode()
        result = migration.build_plan([row], FakeClient(repository()), snapshot=snapshot, snapshot_bytes=raw)
        self.assertEqual(result['source_snapshot_provenance']['sha256'], migration.sha256_bytes(raw))
        changed = copy.deepcopy(snapshot)
        changed['repositories'][0]['default_branch'] = 'changed'
        with self.assertRaisesRegex(migration.MigrationError, 'bytes disagree'):
            migration.build_plan([row], FakeClient(repository()), snapshot=changed, snapshot_bytes=raw)

    def test_malformed_inventory_cannot_be_filtered_to_empty(self):
        client = migration.GhApi()
        for key in (None, 'workflow_runs', 'items'):
            for bad in (None, 7, 'unknown'):
                with self.subTest(key=key, bad=bad):
                    result = [bad] if key is None else {key: [bad]}
                    with patch.object(client, 'request', return_value=result):
                        with self.assertRaisesRegex(migration.ApiError, 'non-object row'):
                            client._list_paginated('fixture', key)

    def test_duplicate_targets_and_source_target_dependencies_rejected(self):
        first = {'source_name': 'source', 'target_name': 'shared', 'action': 'rename'}
        for second in ({'source_name': 'other', 'target_name': 'SHARED', 'action': 'rename'}, {'source_name': 'shared', 'target_name': 'source', 'action': 'rename'}):
            with self.assertRaises(migration.MigrationError):
                migration.build_plan([first, second], FakeClient(repository()))
        first_op = operation()
        second_op = copy.deepcopy(first_op)
        second_op.update(operation_id='rename:AI-Ascension/other->target', source_name='other')
        plan, _, _, _ = apply_plan_fixture(self.root, [first_op, second_op])
        with self.assertRaisesRegex(migration.MigrationError, 'target name'):
            migration.validate_plan(plan)

    def test_duplicate_json_keys_are_rejected(self):
        path = self.root/'duplicate.json'
        path.write_text('{"operations": [], "operations": [1]}')
        with self.assertRaisesRegex(migration.MigrationError, 'Duplicate JSON'):
            migration.read_json(path)
