from __future__ import annotations

import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from publisher import OfflinePublisher, DuplicatePublicationError, source_digest
from publisher.errors import ApprovalError, ProductionGateError, PublisherError, SchemaValidationError, SecurityError
from publisher.security import safe_public_url, safe_relative_path
from publisher.validate import validate_manifest, validate_production_publication


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "publication" / "run.synthetic.json"


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def approved_fixture() -> tuple[dict, dict]:
    manifest = load_fixture()
    manifest.update(
        {
            "title": "Approved report-only local test",
            "recorded_at": "2026-09-07T12:00:00Z",
            "classification": "approved_public",
            "test_fixture": False,
            "approval_reference": "approval-1",
        }
    )
    manifest["model_configuration"] = {
        "identifier": "example-model",
        "provider": "example-provider",
        "revision": "example-revision",
        "calls_measured": 1,
    }
    manifest["action_timeline"].update(status="unavailable", decisions=[])
    manifest["local_guess_reveal"].update(status="unavailable", legal_option_count=0)
    manifest["evidence"]["rights_status"] = "approved"
    manifest["evidence"]["caption_support"] = "exact"
    manifest["resource_budget"]["provider_calls"] = 1
    manifest["disclosures"] = ["Local test record; no production deployment is implied."]
    manifest["source"]["content_digest"] = source_digest(manifest)
    approval = {
        "schema_version": "publication-approval-v1",
        "approval_id": "approval-1",
        "authority_reference": "local-review-record-1",
        "approved_at": "2026-09-07T05:00:00Z",
        "expires_at": None,
        "operation": "publish_run",
        "target": manifest["public_run_id"],
        "source_digest": manifest["source"]["content_digest"],
        "allowed_surfaces": ["run_manifest", "run_page", "decision_timeline", "evidence_panel"],
        "allowed_fields": ["*"],
        "approved_assets": [],
        "scope_notes": "Synthetic local approval shape used only by unit tests.",
        "revoked": False,
    }
    return manifest, approval


class PublicationTests(unittest.TestCase):
    def test_synthetic_fixture_is_valid_for_local_render(self):
        manifest = OfflinePublisher().ingest(FIXTURE)
        self.assertEqual(manifest["schema_version"], "public-run-v2")
        self.assertTrue(manifest["test_fixture"])

    def test_synthetic_fixture_fails_production_gate(self):
        manifest = load_fixture()
        with self.assertRaises(ProductionGateError):
            validate_production_publication(manifest, None)

    def test_private_and_forced_fixture_fail_production_gate(self):
        for classification, evidence_kind in (("private", "report_only"), ("approved_public", "forced_fixture")):
            manifest, approval = approved_fixture()
            manifest["classification"] = classification
            manifest["evidence_kind"] = evidence_kind
            manifest["test_fixture"] = evidence_kind == "forced_fixture"
            manifest["source"]["content_digest"] = source_digest(manifest)
            approval["source_digest"] = manifest["source"]["content_digest"]
            with self.assertRaises(ProductionGateError):
                validate_production_publication(manifest, approval)

    def test_missing_approval_and_forged_authority_boolean_fail(self):
        manifest, _approval = approved_fixture()
        with self.assertRaises(ProductionGateError):
            validate_production_publication(manifest, None)
        forged = {
            "approval_id": "approval-1",
            "is_approved": True,
        }
        with self.assertRaises((SchemaValidationError, SecurityError)):
            from publisher.validate import validate_approval

            validate_approval(forged)

    def test_changed_digest_invalidates_approval(self):
        manifest, approval = approved_fixture()
        manifest["title"] = "Edited after approval"
        with self.assertRaises(PublisherError):
            validate_production_publication(manifest, approval)

    def test_approval_target_digest_and_expiry_are_checked(self):
        manifest, approval = approved_fixture()
        approval["target"] = "other-public-run"
        with self.assertRaises(ApprovalError):
            validate_production_publication(manifest, approval)
        manifest, approval = approved_fixture()
        approval["expires_at"] = "2026-09-07T11:30:00Z"
        with self.assertRaises(ApprovalError):
            validate_production_publication(
                manifest,
                approval,
                now=datetime(2026, 9, 7, 12, 0, tzinfo=timezone.utc),
            )

    def test_revoked_approval_is_rejected(self):
        manifest, approval = approved_fixture()
        approval["revoked"] = True
        with self.assertRaises(ApprovalError):
            validate_production_publication(manifest, approval)

    def test_unknown_fields_and_unsafe_urls_fail_closed(self):
        manifest = load_fixture()
        manifest["unexpected"] = "reject"
        with self.assertRaises(SchemaValidationError):
            validate_manifest(manifest)
        manifest = load_fixture()
        manifest["evidence"]["availability"] = "video"
        manifest["evidence"]["video_url"] = "javascript:alert(1)"
        manifest["source"]["content_digest"] = source_digest(manifest)
        with self.assertRaises(SchemaValidationError):
            validate_manifest(manifest)
        with self.assertRaises(SecurityError):
            safe_public_url("data:text/html,unsafe")
        with self.assertRaises(SecurityError):
            safe_relative_path("../private.json")

    def test_cross_field_timeline_and_evidence_contracts(self):
        manifest = load_fixture()
        manifest["action_timeline"]["decisions"][0]["chosen_action"] = "Discard"
        manifest["source"]["content_digest"] = source_digest(manifest)
        with self.assertRaises(PublisherError):
            validate_manifest(manifest)

    def test_mismatched_provider_call_metadata_is_rejected(self):
        manifest, _approval = approved_fixture()
        manifest["resource_budget"]["provider_calls"] = 2
        manifest["source"]["content_digest"] = source_digest(manifest)
        with self.assertRaises(PublisherError):
            validate_manifest(manifest)
        manifest = load_fixture()
        manifest["evidence"]["availability"] = "video"
        manifest["source"]["content_digest"] = source_digest(manifest)
        with self.assertRaises(PublisherError):
            validate_manifest(manifest)

    def test_render_escapes_record_text_and_is_idempotent(self):
        publisher = OfflinePublisher()
        before = FIXTURE.read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            first = publisher.render(FIXTURE, output)
            second = publisher.render(FIXTURE, output)
            self.assertFalse(first.idempotent)
            self.assertTrue(second.idempotent)
            page = first.html_path.read_text(encoding="utf-8")
            self.assertIn("&lt;fixture&gt;", page)
            self.assertNotIn("<script", page.casefold())
            self.assertIn("Synthetic fixture", page)
        self.assertEqual(before, FIXTURE.read_bytes())

    def test_production_publish_is_local_and_duplicate_version_is_rejected(self):
        manifest, approval = approved_fixture()
        publisher = OfflinePublisher()
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as output_temp:
            temp_path = Path(temp)
            manifest_path = temp_path / "manifest.json"
            approval_path = temp_path / "approval.json"
            # The output root is outside the input tree by contract.
            out = Path(output_temp)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            approval_path.write_text(json.dumps(approval), encoding="utf-8")
            result = publisher.publish(manifest_path, approval_path, out)
            repeat = publisher.publish(manifest_path, approval_path, out)
            self.assertTrue(repeat.idempotent)
            self.assertEqual(result.source_digest, manifest["source"]["content_digest"])
            changed = copy.deepcopy(manifest)
            changed["title"] = "Different version content"
            changed["source"]["content_digest"] = source_digest(changed)
            changed["approval_reference"] = approval["approval_id"]
            changed_path = temp_path / "changed.json"
            changed_path.write_text(json.dumps(changed), encoding="utf-8")
            approval["source_digest"] = changed["source"]["content_digest"]
            approval_path.write_text(json.dumps(approval), encoding="utf-8")
            with self.assertRaises(DuplicatePublicationError):
                publisher.publish(changed_path, approval_path, out)

    def test_output_must_be_separate_from_input(self):
        with self.assertRaises(SecurityError):
            OfflinePublisher().render(FIXTURE, FIXTURE.parent)

    def test_hidden_and_symlink_artifacts_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".hidden.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(SecurityError):
                OfflinePublisher().verify_artifact_root(root)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            hidden_root = root / ".artifacts"
            hidden_root.mkdir()
            with self.assertRaises(SecurityError):
                OfflinePublisher().verify_artifact_root(hidden_root)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "target.json"
            target.write_text("{}", encoding="utf-8")
            link = root / "link.json"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            with self.assertRaises(SecurityError):
                OfflinePublisher().verify_artifact_root(root)

    def test_symlink_inside_output_tree_is_rejected(self):
        manifest, approval = approved_fixture()
        with tempfile.TemporaryDirectory() as source_temp, tempfile.TemporaryDirectory() as output_temp:
            source_root = Path(source_temp)
            output_root = Path(output_temp)
            manifest_path = source_root / "manifest.json"
            approval_path = source_root / "approval.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            approval_path.write_text(json.dumps(approval), encoding="utf-8")
            (output_root / "run-manifests").symlink_to(source_root, target_is_directory=True)
            with self.assertRaises(SecurityError):
                OfflinePublisher().publish(manifest_path, approval_path, output_root)

    def test_symlinked_input_ancestor_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "real"
            target.mkdir()
            (target / "manifest.json").write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
            alias = root / "alias"
            try:
                alias.symlink_to(target, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            with self.assertRaises(SecurityError):
                OfflinePublisher().ingest(alias / "manifest.json")


if __name__ == "__main__":
    unittest.main()
