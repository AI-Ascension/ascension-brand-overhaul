import copy
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from tests.test_migration_tooling import FakeClient, migration, operation, repository


def absent(name="target"):
    return {"exists": False, "owner": migration.DEFAULT_OWNER, "name": name}


class MultiFakeClient:
    def __init__(self, states, *, rename_error=None):
        self.states = {name: copy.deepcopy(value) for name, value in states.items()}
        self.rename_error = rename_error
        self.rename_calls = []

    def current_user(self):
        return {"login": "root-operator", "id": 1}

    def observe_repo(self, owner, name):
        value = self.states.get(name)
        if value is None:
            return {"exists": False, "owner": owner, "name": name}
        return copy.deepcopy(value)

    def rename_repo(self, owner, source_name, target_name):
        self.rename_calls.append((owner, source_name, target_name))
        if self.rename_error is not None:
            raise self.rename_error
        value = self.states.pop(source_name)
        value["name"] = target_name
        value["full_name"] = f"{owner}/{target_name}"
        self.states[target_name] = value
        return copy.deepcopy(value)


def apply_plan_fixture(root, ops):
    plan_path = root / "plan.json"
    receipt_path = root / "receipt.json"
    plan = {
        "schema_version": migration.SCHEMA_VERSION,
        "mode": "dry_run",
        "generated_at": "2026-09-07T00:00:00Z",
        "operator": {"owner_notification_authorized": False},
        "source_snapshot_provenance": {"provided": False, "schema_version": None, "sha256": None},
        "operations": ops,
    }
    migration.write_json(plan_path, plan)
    approval = {
        "schema_version": migration.APPROVAL_SCHEMA_VERSION,
        "plan_sha256": migration.sha256_bytes(plan_path.read_bytes()),
        "approved_by": "root-operator",
        "approved_at": "2026-09-07T00:00:00Z",
        "operation_ids": [item["operation_id"] for item in ops],
        "owner_notification_authorized": False,
    }
    return plan, plan_path, receipt_path, approval


class MigrationReviewGateTests(unittest.TestCase):
    def test_recorded_branch_and_visibility_preconditions_are_hard_gates(self):
        op = operation()
        op["preconditions"]["expected_default_branch"] = "develop"
        op["preconditions"]["expected_visibility"] = "private"
        result = migration.evaluate_operation(op, repository(), absent(), authorized=True)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["gates"]["default_branch"]["code"], "stale_default_branch")
        self.assertEqual(result["gates"]["visibility"]["code"], "stale_visibility")

    def test_generated_plan_embeds_and_checks_immutable_backup(self):
        source = repository()
        plan = migration.build_plan(
            [{"source_name": "source", "target_name": "target", "action": "rename"}],
            FakeClient(source),
            observed_at="2026-09-07T00:00:00Z",
        )
        op = plan["operations"][0]
        reference = op["backup_reference"]
        self.assertTrue(reference["immutable"])
        self.assertEqual(reference["snapshot_sha256"], migration.sha256_json(reference["snapshot"]))
        self.assertEqual(op["preflight"]["gates"]["backup"]["status"], "pass")
        migration.validate_plan(plan)

        reference["snapshot"]["head_sha"] = "f" * 40
        result = migration.evaluate_operation(op, source, absent(), authorized=True)
        self.assertIn("backup_reference_digest_invalid", result["blockers"])

    def test_missing_backup_reference_blocks_authorized_rename(self):
        op = operation()
        del op["backup_reference"]
        result = migration.evaluate_operation(op, repository(), absent(), authorized=True)
        self.assertIn("backup_reference_missing", result["blockers"])


class FakePagedGhApi(migration.GhApi):
    def __init__(self):
        super().__init__(executable="fake-gh")
        self.calls = []

    def request(self, method, path, body=None):
        self.calls.append((method, path))
        if path == "repos/AI-Ascension/source":
            return {
                "id": 10,
                "name": "source",
                "full_name": "AI-Ascension/source",
                "default_branch": "main",
                "visibility": "public",
                "archived": False,
            }
        if path == "repos/AI-Ascension/source/branches/main":
            return {"protected": False, "commit": {"sha": "a" * 40}}
        if path == "repos/AI-Ascension/source/actions/workflows?per_page=100":
            return {"workflows": []}
        if "/actions/runs?" in path:
            query = parse_qs(urlparse(path).query)
            status = query["status"][0]
            return {
                "workflow_runs": (
                    [{"id": len(status), "status": status}]
                    if status in {"queued", "waiting"}
                    else []
                )
            }
        if "/pulls?" in path:
            page = parse_qs(urlparse(path).query).get("page", ["1"])[0]
            if page == "1":
                return [{"number": number} for number in range(1, 101)]
            return [{"number": 101}]
        if path.startswith("search/code?"):
            page = parse_qs(urlparse(path).query).get("page", ["1"])[0]
            if page == "1":
                return {
                    "total_count": 101,
                    "items": [
                        {
                            "repository": {"full_name": "AI-Ascension/other"},
                            "path": ".github/workflows/workflow.yml",
                        }
                        for _ in range(100)
                    ],
                }
            return {
                "total_count": 101,
                "items": [
                    {
                        "repository": {"full_name": "AI-Ascension/consumer"},
                        "path": ".github/workflows/use.yml",
                    }
                ],
            }
        if "/contents/" in path:
            raise migration.ApiError("HTTP 404 Not Found", status_code=404)
        if path.endswith("/pages"):
            raise migration.ApiError("HTTP 404 Not Found", status_code=404)
        raise AssertionError(f"unexpected fake API path: {path}")


class MigrationReviewApiTests(unittest.TestCase):
    def test_404_is_endpoint_specific_unknown(self):
        calls = []

        def fake_run(args, **kwargs):
            path = args[2]
            calls.append(path)
            if path == "repos/AI-Ascension/source":
                payload = {
                    "id": 10,
                    "name": "source",
                    "full_name": "AI-Ascension/source",
                    "default_branch": "main",
                    "visibility": "public",
                    "archived": False,
                }
                return SimpleNamespace(returncode=0, stdout=json.dumps(payload).encode(), stderr=b"")
            if path == "repos/AI-Ascension/source/branches/main":
                payload = {"protected": True, "commit": {"sha": "a" * 40}}
                return SimpleNamespace(returncode=0, stdout=json.dumps(payload).encode(), stderr=b"")
            if path.endswith("/protection"):
                payload = {"required_status_checks": {"strict": True}}
                return SimpleNamespace(returncode=0, stdout=json.dumps(payload).encode(), stderr=b"")
            return SimpleNamespace(returncode=1, stdout=b"", stderr=b"HTTP 404 Not Found")

        with patch.object(migration.subprocess, "run", side_effect=fake_run):
            api = migration.GhApi(executable="fake-gh")
            with self.assertRaises(migration.ApiError) as raised:
                api.request("GET", "repos/AI-Ascension/source/pages")
            self.assertEqual(raised.exception.status_code, 404)
            observed = api.observe_repo("AI-Ascension", "source")

        self.assertFalse(observed["pages_available"])
        self.assertFalse(observed["workflow_read_available"])
        self.assertFalse(observed["pull_read_available"])
        self.assertFalse(observed["action_consumers_known"])
        self.assertFalse(observed["hosted_action"])
        self.assertIn("active-runs[queued]", observed["workflow_error"])
        evaluation = migration.evaluate_operation(operation(), observed, absent(), authorized=True)
        self.assertIn("active_work_inventory_unavailable", evaluation["blockers"])
        self.assertIn("pages_configuration_unavailable", evaluation["blockers"])
        self.assertIn("hosted_action_consumers_unavailable", evaluation["blockers"])
        self.assertIn("repos/AI-Ascension/source/pages", calls)

    def test_all_active_statuses_and_full_pages_are_inventory_inputs(self):
        api = FakePagedGhApi()
        observed = api.observe_repo("AI-Ascension", "source")
        run_paths = [path for _, path in api.calls if "/actions/runs?" in path]
        self.assertEqual(
            {parse_qs(urlparse(path).query)["status"][0] for path in run_paths},
            set(migration.ACTIVE_RUN_STATUSES),
        )
        self.assertTrue(any("/pulls?state=open&per_page=100&page=2" in path for _, path in api.calls))
        self.assertTrue(any("search/code?" in path and "page=2" in path for _, path in api.calls))
        self.assertEqual(len(observed["open_pull_requests"]), 101)
        self.assertEqual({run["status"] for run in observed["active_runs"]}, {"queued", "waiting"})
        self.assertTrue(any(item["repository"] == "AI-Ascension/consumer" for item in observed["action_consumers"]))

    def test_search_total_count_gap_is_unknown(self):
        class IncompleteSearchApi(FakePagedGhApi):
            def request(self, method, path, body=None):
                if path.startswith("search/code?"):
                    self.calls.append((method, path))
                    return {"total_count": 101, "items": [{"repository": {"full_name": "AI-Ascension/other"}}]}
                return super().request(method, path, body)

        api = IncompleteSearchApi()
        consumers, known, error = api._action_consumers("AI-Ascension", "source")
        self.assertEqual(consumers, [])
        self.assertFalse(known)
        self.assertIn("incomplete", error)


class MigrationReviewApplyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_ambiguous_transport_is_unknown_and_halts_the_operation_set(self):
        ops = [
            operation(),
            operation(source_name="source2", target_name="target2", repo_id=11, head="b" * 40),
        ]
        states = {"source": repository(), "source2": repository(name="source2", repo_id=11, head="b" * 40)}
        for failure in (ConnectionResetError("connection reset by peer"), migration.ApiError("upstream", status_code=502)):
            with self.subTest(failure=type(failure).__name__):
                plan, plan_path, receipt_path, approval = apply_plan_fixture(self.root / type(failure).__name__, ops)
                client = MultiFakeClient(states, rename_error=failure)
                first = migration.apply_plan(
                    plan, client, plan_path=plan_path, receipt_path=receipt_path, approval=approval, apply=True
                )
                self.assertEqual(first["operations"][0]["status"], "unknown")
                self.assertEqual(len(first["operations"]), 1)
                self.assertEqual(len(client.rename_calls), 1)
                second = migration.apply_plan(
                    plan, client, plan_path=plan_path, receipt_path=receipt_path, approval=approval, apply=True
                )
                self.assertEqual(second["operations"][0]["status"], "unknown_waiting_for_reconciliation")
                self.assertEqual(len(client.rename_calls), 1)

    def test_stale_applied_receipt_is_rechecked_before_any_retry(self):
        source = repository()
        client = FakeClient(source)
        plan, plan_path, receipt_path, approval = apply_plan_fixture(self.root / "stale", [operation()])
        first = migration.apply_plan(
            plan, client, plan_path=plan_path, receipt_path=receipt_path, approval=approval, apply=True
        )
        self.assertEqual(first["operations"][0]["status"], "applied")
        client.states["target"]["id"] = 999
        second = migration.apply_plan(
            plan, client, plan_path=plan_path, receipt_path=receipt_path, approval=approval, apply=True
        )
        self.assertNotEqual(second["operations"][0]["status"], "applied")
        self.assertEqual(len(client.rename_calls), 1)

    def test_approval_is_bound_to_actor_scope_and_all_rename_ids(self):
        source = repository()
        client = FakeClient(source)
        plan, plan_path, receipt_path, approval = apply_plan_fixture(self.root / "authority", [operation()])
        bad_actor = dict(approval, approved_by="arbitrary-operator")
        with self.assertRaisesRegex(migration.MigrationError, "actor"):
            migration.apply_plan(plan, client, plan_path=plan_path, receipt_path=receipt_path, approval=bad_actor, apply=True)

        missing_ids = dict(approval, operation_ids=[])
        with self.assertRaisesRegex(migration.MigrationError, "every rename"):
            migration.apply_plan(plan, client, plan_path=plan_path, receipt_path=receipt_path, approval=missing_ids, apply=True)

        with self.assertRaisesRegex(migration.MigrationError, "approved migration scope"):
            migration.build_plan(
                [{"owner": "OtherOrg", "source_name": "source", "target_name": "target", "action": "rename"}],
                client,
            )


class MigrationReviewIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_operation_set_lock_covers_any_receipt_path(self):
        plan, plan_path, receipt_path, approval = apply_plan_fixture(self.root / "locks", [operation()])
        digest = migration.sha256_bytes(plan_path.read_bytes())
        operation_lock = migration.operation_set_lock_path(plan_path, digest)
        operation_lock.parent.mkdir(parents=True, exist_ok=True)
        self.addCleanup(operation_lock.unlink, missing_ok=True)
        operation_lock.write_text("another active operator\n", encoding="utf-8")
        alternate_receipt = self.root / "locks" / "receipt-two.json"
        client = FakeClient(repository())
        with self.assertRaisesRegex(migration.MigrationError, "Operation set is locked"):
            migration.apply_plan(
                plan, client, plan_path=plan_path, receipt_path=alternate_receipt, approval=approval, apply=True
            )
        self.assertEqual(client.rename_calls, [])
        self.assertTrue(operation_lock.exists())
        self.assertFalse(receipt_path.exists())

    def test_snapshot_identity_and_exact_file_digest_are_required(self):
        valid = {
            "schema_version": "ai-ascension.source-snapshot.v1",
            "collection_date": "2026-09-07",
            "repositories": [
                {
                    "stable_id": 10,
                    "full_name": "AI-Ascension/source",
                    "default_branch": "main",
                    "default_head": "a" * 40,
                    "visibility": "public",
                }
            ],
        }
        duplicate_name = copy.deepcopy(valid)
        duplicate_name["repositories"].append(
            {"stable_id": 11, "full_name": "ai-ascension/SOURCE", "default_branch": "main", "default_head": "b" * 40}
        )
        with self.assertRaisesRegex(migration.MigrationError, "repeats"):
            migration.validate_snapshot(duplicate_name)
        duplicate_id = copy.deepcopy(valid)
        duplicate_id["repositories"].append(
            {"stable_id": 10, "full_name": "AI-Ascension/other", "default_branch": "main", "default_head": "b" * 40}
        )
        with self.assertRaisesRegex(migration.MigrationError, "stable_id"):
            migration.validate_snapshot(duplicate_id)

        snapshot_path = self.root / "source-snapshot.json"
        migration.write_json(snapshot_path, valid)
        digest = migration.sha256_bytes(snapshot_path.read_bytes())
        plan = migration.build_plan(
            [{"source_name": "source", "target_name": "target", "action": "rename", "stable_repository_id": 10}],
            FakeClient(repository()),
            snapshot=valid,
            snapshot_sha256=digest,
            snapshot_bytes=snapshot_path.read_bytes(),
            observed_at="2026-09-07T00:00:00Z",
        )
        self.assertEqual(plan["source_snapshot_provenance"]["sha256"], digest)
        self.assertEqual(plan["source_snapshot_provenance"]["schema_version"], valid["schema_version"])
        migration.validate_plan(plan)

        conflicting_map = [{"source_name": "source", "target_name": "target", "action": "rename", "stable_repository_id": 11}]
        with self.assertRaisesRegex(migration.MigrationError, "disagrees"):
            migration.build_plan(conflicting_map, FakeClient(repository()), snapshot=valid)

        bad_plan = copy.deepcopy(plan)
        bad_plan["source_snapshot_provenance"]["sha256"] = "not-a-digest"
        with self.assertRaisesRegex(migration.MigrationError, "source snapshot digest"):
            migration.validate_plan(bad_plan)


if __name__ == "__main__":
    unittest.main()
