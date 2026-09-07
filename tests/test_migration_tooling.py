import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "migration" / "tooling" / "github_migration.py"
spec = importlib.util.spec_from_file_location("github_migration", MODULE_PATH)
migration = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(migration)


def repository(name="source", repo_id=10, head="a" * 40, **overrides):
    protection = {
        "branch_protected": True,
        "configuration": {"required_status_checks": {"strict": True}},
        "available": True,
        "error": None,
    }
    result = {
        "exists": True,
        "owner": "AI-Ascension",
        "name": name,
        "full_name": f"AI-Ascension/{name}",
        "id": repo_id,
        "default_branch": "main",
        "head_sha": head,
        "visibility": "public",
        "archived": False,
        "branch_protected": True,
        "protected_configuration": protection,
        "pages": None,
        "pages_available": True,
        "pages_error": None,
        "workflows": [],
        "active_runs": [],
        "workflow_read_available": True,
        "workflow_error": None,
        "open_pull_requests": [],
        "pull_read_available": True,
        "pull_error": None,
        "active_run_statuses": list(migration.ACTIVE_RUN_STATUSES),
        "hosted_action": False,
        "action_consumers": [],
        "action_consumers_known": True,
        "action_consumers_error": None,
    }
    result.update(overrides)
    return result


def operation(source_name="source", target_name="target", repo_id=10, head="a" * 40, **overrides):
    source = repository(name=source_name, head=head)
    protection = source["protected_configuration"]
    backup = migration.compact_repo(source)
    result = {
        "operation_id": f"rename:AI-Ascension/{source_name}->{target_name}",
        "owner": "AI-Ascension",
        "source_name": source_name,
        "target_name": target_name,
        "action": "rename",
        "backup_reference": {
            "kind": "test_embedded_repository_metadata",
            "immutable": True,
            "snapshot_sha256": migration.sha256_json(backup),
            "snapshot": backup,
            "captured_at": "2026-09-07T00:00:00Z",
        },
        "preconditions": {
            "expected_stable_repository_id": repo_id,
            "expected_current_head": head,
            "expected_default_branch": "main",
            "expected_visibility": "public",
            "protected_configuration": {
                "digest": migration.sha256_json(protection),
                "observed": migration.compact_repo(repository(head=head))["protected_configuration"],
            },
        },
        "rollback": {"preconditions": ["source name is available", "target identity is re-read"]},
    }
    result.update(overrides)
    return result


class FakeClient:
    def __init__(self, source, target=None, *, verification=None, rename_error=None):
        self.states = {source["name"]: copy.deepcopy(source)}
        if target is not None:
            self.states[target["name"]] = copy.deepcopy(target)
        self.verification = verification
        self.rename_error = rename_error
        self.rename_calls = []

    def current_user(self):
        return {"login": "root-operator", "id": 1}

    def observe_repo(self, owner, name):
        if self.verification is not None and name == self.verification["name"] and name in self.states:
            return copy.deepcopy(self.verification)
        state = self.states.get(name)
        return copy.deepcopy(state) if state is not None else {"exists": False, "owner": owner, "name": name}

    def rename_repo(self, owner, source_name, target_name):
        self.rename_calls.append((owner, source_name, target_name))
        if self.rename_error is not None:
            raise self.rename_error
        source = self.states.pop(source_name)
        source["name"] = target_name
        source["full_name"] = f"{owner}/{target_name}"
        self.states[target_name] = source
        return source


class MigrationGateTests(unittest.TestCase):
    def test_stale_stable_id_blocks_before_any_other_gate(self):
        source = repository(repo_id=11)
        result = migration.evaluate_operation(operation(repo_id=10), source, {"exists": False}, authorized=False)
        self.assertIn("stale_stable_repository_id", result["blockers"])
        self.assertEqual(result["gates"]["stable_identity"]["status"], "blocked")

    def test_stale_head_is_detected(self):
        source = repository(head="b" * 40)
        result = migration.evaluate_operation(operation(head="a" * 40), source, {"exists": False}, authorized=False)
        self.assertIn("stale_current_head", result["blockers"])
        self.assertEqual(result["gates"]["current_head"]["code"], "stale_current_head")

    def test_changed_protected_configuration_is_detected(self):
        source = repository()
        source["protected_configuration"]["configuration"]["required_status_checks"]["strict"] = False
        result = migration.evaluate_operation(operation(), source, {"exists": False}, authorized=False)
        self.assertIn("stale_protected_configuration", result["blockers"])

    def test_target_collision_is_hard_block(self):
        source = repository()
        target = repository(name="target", repo_id=99, head="c" * 40)
        result = migration.evaluate_operation(operation(), source, target, authorized=False)
        self.assertIn("target_name_collision", result["blockers"])
        self.assertEqual(result["gates"]["target_collision"]["code"], "target_name_collision")

    def test_hosted_action_consumers_are_blocked(self):
        source = repository(action_consumers=[{"repository": "AI-Ascension/consumer", "path": ".github/workflows/build.yml"}])
        result = migration.evaluate_operation(operation(), source, {"exists": False}, authorized=False)
        self.assertIn("hosted_action_consumers_found", result["blockers"])

    def test_active_pull_request_and_run_are_blocked(self):
        source = repository(
            open_pull_requests=[{"number": 3, "head": {"sha": "d" * 40}}],
            active_runs=[{"id": 4, "status": "in_progress"}],
        )
        result = migration.evaluate_operation(operation(), source, {"exists": False}, authorized=False)
        self.assertIn("active_work_present", result["blockers"])

    def test_pages_requires_preservation_review(self):
        source = repository(pages={"url": "https://example.github.io", "cname": None})
        result = migration.evaluate_operation(operation(), source, {"exists": False}, authorized=False)
        self.assertIn("pages_requires_custom_domain_check", result["blockers"])

    def test_unknown_protected_or_action_state_is_not_a_pass(self):
        source = repository(
            protected_configuration={"available": False, "error": "forbidden"},
            action_consumers_known=False,
            action_consumers_error="forbidden",
            workflow_read_available=False,
        )
        result = migration.evaluate_operation(operation(), source, {"exists": False}, authorized=False)
        self.assertIn("protected_configuration_unavailable", result["blockers"])
        self.assertIn("hosted_action_consumers_unavailable", result["blockers"])
        self.assertIn("active_work_inventory_unavailable", result["blockers"])

    def test_deferred_map_assignment_is_explicit(self):
        source = repository(name="ascension-map-visualizer")
        op = operation(source_name="ascension-map-visualizer", target_name="sts2-map", action="deferred-rename")
        result = migration.evaluate_operation(op, source, {"exists": False}, authorized=True)
        self.assertEqual(result["status"], "deferred")
        self.assertEqual(result["gates"]["active_work"]["code"], "active_assignment_pins_original_name")


class MigrationApplyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plan_path = self.root / "plan.json"
        self.receipt_path = self.root / "receipt.json"
        self.source = repository()
        self.target = {"exists": False, "owner": "AI-Ascension", "name": "target"}
        self.op = operation()
        self.plan = {
            "schema_version": migration.SCHEMA_VERSION,
            "mode": "dry_run",
            "generated_at": "2026-09-07T00:00:00Z",
            "operator": {"owner_notification_authorized": False},
            "source_snapshot_provenance": {"provided": False, "schema_version": None, "sha256": None},
            "operations": [self.op],
        }
        migration.write_json(self.plan_path, self.plan)
        self.approval = {
            "schema_version": migration.APPROVAL_SCHEMA_VERSION,
            "plan_sha256": migration.sha256_bytes(self.plan_path.read_bytes()),
            "approved_by": "root-operator",
            "approved_at": "2026-09-07T00:00:00Z",
            "operation_ids": [self.op["operation_id"]],
            "owner_notification_authorized": False,
        }

    def test_remote_apply_requires_separate_approval(self):
        with self.assertRaisesRegex(migration.MigrationError, "approval"):
            migration.apply_plan(self.plan, FakeClient(self.source), plan_path=self.plan_path, receipt_path=self.receipt_path, apply=True)
        self.assertFalse(self.receipt_path.exists())

    def test_dry_run_has_no_mutation(self):
        client = FakeClient(self.source)
        receipt = migration.apply_plan(self.plan, client, plan_path=self.plan_path, receipt_path=self.receipt_path, apply=False)
        self.assertEqual(receipt["operations"][0]["status"], "dry_run_blocked")
        self.assertEqual(client.rename_calls, [])

    def test_approved_apply_is_read_after_write_verified_and_repeatable(self):
        client = FakeClient(self.source)
        first = migration.apply_plan(self.plan, client, plan_path=self.plan_path, receipt_path=self.receipt_path, approval=self.approval, apply=True)
        self.assertEqual(first["operations"][0]["status"], "applied")
        self.assertEqual(len(client.rename_calls), 1)
        second = migration.apply_plan(self.plan, client, plan_path=self.plan_path, receipt_path=self.receipt_path, approval=self.approval, apply=True)
        self.assertEqual(second["operations"][0]["status"], "applied")
        self.assertEqual(len(client.rename_calls), 1)

    def test_already_renamed_expected_id_is_idempotent_without_approval(self):
        client = FakeClient(self.source)
        migration.apply_plan(self.plan, client, plan_path=self.plan_path, receipt_path=self.receipt_path, approval=self.approval, apply=True)
        receipt = migration.apply_plan(self.plan, client, plan_path=self.plan_path, receipt_path=self.root / "second.json", apply=False)
        self.assertEqual(receipt["operations"][0]["status"], "already_satisfied")

    def test_verification_failure_records_rollback_preconditions(self):
        wrong = repository(name="target", repo_id=999, head="z" * 40)
        client = FakeClient(self.source, verification=wrong)
        receipt = migration.apply_plan(self.plan, client, plan_path=self.plan_path, receipt_path=self.receipt_path, approval=self.approval, apply=True)
        self.assertEqual(receipt["operations"][0]["status"], "verification_failed")
        self.assertEqual(receipt["operations"][0]["rollback_decision"], "do_not_rollback_automatically")
        self.assertTrue(receipt["operations"][0]["rollback_preconditions"])

    def test_unknown_response_waits_for_explicit_reconciliation_retry(self):
        client = FakeClient(self.source, rename_error=migration.ApiError("GitHub API request failed: timeout"))
        first = migration.apply_plan(self.plan, client, plan_path=self.plan_path, receipt_path=self.receipt_path, approval=self.approval, apply=True)
        self.assertEqual(first["operations"][0]["status"], "unknown")
        second = migration.apply_plan(self.plan, client, plan_path=self.plan_path, receipt_path=self.receipt_path, approval=self.approval, apply=True)
        self.assertEqual(second["operations"][0]["status"], "unknown_waiting_for_reconciliation")
        third = migration.apply_plan(self.plan, client, plan_path=self.plan_path, receipt_path=self.receipt_path, approval=self.approval, apply=True)
        self.assertEqual(third["operations"][0]["status"], "unknown_waiting_for_reconciliation")
        self.assertEqual(len(client.rename_calls), 1)

    def test_pending_attempt_survives_interruption_before_response(self):
        client = FakeClient(self.source)
        def interrupted(*args):
            saved = migration.read_json(self.receipt_path)
            self.assertEqual(saved['operations'][0]['status'], 'unknown')
            raise KeyboardInterrupt('simulated interrupted request')
        client.rename_repo = interrupted
        with self.assertRaises(KeyboardInterrupt):
            migration.apply_plan(self.plan, client, plan_path=self.plan_path, receipt_path=self.receipt_path, approval=self.approval, apply=True)
        retry_client = FakeClient(self.source)
        receipt = migration.apply_plan(self.plan, retry_client, plan_path=self.plan_path, receipt_path=self.receipt_path, approval=self.approval, apply=True)
        self.assertEqual(receipt['operations'][0]['status'], 'unknown_waiting_for_reconciliation')
        self.assertEqual(retry_client.rename_calls, [])

    def test_receipt_from_other_plan_is_rejected(self):
        client = FakeClient(self.source)
        migration.apply_plan(self.plan, client, plan_path=self.plan_path, receipt_path=self.receipt_path, apply=False)
        receipt = migration.read_json(self.receipt_path)
        receipt['plan_sha256'] = '0' * 64
        migration.write_json(self.receipt_path, receipt)
        with self.assertRaisesRegex(migration.MigrationError, 'different plan'):
            migration.apply_plan(self.plan, client, plan_path=self.plan_path, receipt_path=self.receipt_path, approval=self.approval, apply=True)
        self.assertEqual(client.rename_calls, [])

    def test_receipt_lock_prevents_concurrent_request(self):
        client = FakeClient(self.source)
        lock = self.receipt_path.with_name(self.receipt_path.name + '.lock')
        lock.write_text('another active operator')
        with self.assertRaisesRegex(migration.MigrationError, 'locked'):
            migration.apply_plan(self.plan, client, plan_path=self.plan_path, receipt_path=self.receipt_path, approval=self.approval, apply=True)
        self.assertEqual(client.rename_calls, [])
        self.assertEqual(lock.read_text(), 'another active operator')

    def test_load_approval_rejects_plan_digest_or_owner_notification(self):
        bad = dict(self.approval, plan_sha256="0" * 64)
        bad_path = self.root / "bad.json"
        migration.write_json(bad_path, bad)
        with self.assertRaisesRegex(migration.MigrationError, "exact plan"):
            migration.load_approval(bad_path, self.plan_path, self.plan)
        bad = dict(self.approval, owner_notification_authorized=True)
        migration.write_json(bad_path, bad)
        with self.assertRaisesRegex(migration.MigrationError, "notification"):
            migration.load_approval(bad_path, self.plan_path, self.plan)


if __name__ == "__main__":
    unittest.main()
