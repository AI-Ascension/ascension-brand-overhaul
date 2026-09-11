from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from publisher.capabilities import load_capability_registry, render_capabilities
from publisher.comparison import validate_comparison
from publisher.errors import PublisherError, SchemaValidationError, SecurityError
from publisher.events import aggregate_events, load_event_contract, validate_event
from tests.measurement_scope_helper import scope_fixture, trusted_scope


ROOT = Path(__file__).resolve().parents[1]
EVENT_FIXTURE = ROOT / "tests" / "fixtures" / "publication" / "events.synthetic.json"
CAPABILITY_FIXTURE = ROOT / "tests" / "fixtures" / "publication" / "capabilities.synthetic.json"
COMPARISON_FIXTURE = ROOT / "tests" / "fixtures" / "publication" / "comparison.synthetic.json"


def event_fixture() -> list[dict]:
    return json.loads(EVENT_FIXTURE.read_text(encoding="utf-8"))


class MeasurementTests(unittest.TestCase):
    def test_event_contract_contains_required_concepts_and_is_strict(self):
        contract = load_event_contract()
        names = {event["name"] for event in contract["events"]}
        self.assertEqual(
            names,
            {
                "run_page_view", "media_start", "meaningful_watch_or_read", "decision_presented",
                "decision_guess", "decision_reveal", "evidence_open", "replay_download", "build_start",
                "quickstart_success", "docs_error", "subscribe_confirmed", "unsubscribe_completed",
            },
        )
        event = event_fixture()[0]
        event["email"] = "person@example.invalid"
        with self.assertRaises((SchemaValidationError, SecurityError)):
            validate_event(event, contract=contract)

    def test_consent_server_and_timestamp_gates(self):
        contract = load_event_contract()
        guess = {
            "schema_version": "event-v1", "event_id": "guess-event", "event_name": "decision_guess",
            "surface": "run", "occurred_at": "2026-09-07T12:00:00Z", "timestamp_precision": "minute",
            "content_id": "synthetic-local-run", "campaign_tag": None, "consent_state": "not_collected",
            "coarse_cohort": None, "server_observation": "none", "environment": "synthetic",
            "properties": {"decision_id": "synthetic-decision-1", "option_position": 0},
        }
        with self.assertRaises(PublisherError):
            validate_event(guess, contract=contract)
        guess["consent_state"] = "granted"
        guess["occurred_at"] = "2026-09-07T12:00:01Z"
        with self.assertRaises(PublisherError):
            validate_event(guess, contract=contract)
        success = copy.deepcopy(guess)
        success.update({"event_id": "success-event", "event_name": "quickstart_success", "surface": "build"})
        success["occurred_at"] = "2026-09-07T12:00:00Z"
        success["properties"] = {"workflow": "quickstart", "status": "completed"}
        with self.assertRaises(PublisherError):
            validate_event(success, contract=contract)
        success["server_observation"] = "confirmed"
        self.assertIs(validate_event(success, contract=contract), success)

    def test_event_surface_and_consent_bucket_match_contract(self):
        event = event_fixture()[0]
        event["surface"] = "watch"
        with self.assertRaises(PublisherError):
            validate_event(event)
        event = event_fixture()[0]
        event.update({"consent_state": "granted", "coarse_cohort": {"kind": "consented_cohort", "value": None}})
        with self.assertRaises(PublisherError):
            validate_event(event)

    def test_synthetic_events_do_not_become_production_observations(self):
        events = event_fixture()
        production = aggregate_events(events)
        self.assertIsNone(production["event_count"])
        self.assertTrue(all(metric["state"] == "no_observations" for metric in production["metrics"].values()))
        local = aggregate_events(events, include_synthetic=True)
        self.assertEqual(local["environment"], "synthetic")

    def test_empty_data_is_absent_and_observed_zero_is_distinct(self):
        empty = aggregate_events([])
        self.assertIsNone(empty["event_count"])
        self.assertTrue(all(metric["value"] is None for metric in empty["metrics"].values()))
        events = event_fixture()
        events.append(
            {
                "schema_version": "event-v1", "event_id": "watch-event", "event_name": "meaningful_watch_or_read",
                "surface": "watch", "occurred_at": "2026-09-07T12:02:00Z", "timestamp_precision": "minute",
                "content_id": "synthetic-local-run", "campaign_tag": None, "consent_state": "not_collected",
                "coarse_cohort": None, "server_observation": "none", "environment": "production",
                "properties": {"media_kind": "report"},
            }
        )
        events[0]["environment"] = "production"
        receipt = scope_fixture(events)
        with trusted_scope(receipt):
            result = aggregate_events(events, scope_receipt=receipt)
        self.assertEqual(result["metrics"]["audience-engagement-rate"]["value"], 1.0)

    def test_w01_capability_envelope_preserves_exact_source_ids(self):
        from tests.capability_envelope_helper import capability_envelope
        source_record = json.loads(CAPABILITY_FIXTURE.read_text(encoding="utf-8"))[0]
        source_record["capability_id"] = "CAP-ORG-POLICY"
        envelope = capability_envelope([source_record])
        envelope["source_snapshot"] = "execution/source-snapshot.json"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "capabilities.json"
            path.write_text(json.dumps(envelope), encoding="utf-8")
            records, metadata = load_capability_registry(path)
        self.assertEqual(records[0]["capability_id"], "CAP-ORG-POLICY")
        self.assertEqual(metadata["source_snapshot"], "execution/source-snapshot.json")

    def test_capability_render_escapes_text_and_preserves_distinct_states(self):
        records = json.loads(CAPABILITY_FIXTURE.read_text(encoding="utf-8"))
        records[0]["claim"] = "<untrusted claim>"
        page = render_capabilities(records)
        self.assertIn("&lt;untrusted claim&gt;", page)
        self.assertIn("offline_test", page)
        self.assertIn("No observation date", page)

    def test_comparison_requires_declared_matching_context_and_disables_ranking(self):
        comparison = json.loads(COMPARISON_FIXTURE.read_text(encoding="utf-8"))
        self.assertIs(validate_comparison(comparison), comparison)
        comparison["runs"][1]["budget"] = "different budget"
        with self.assertRaises(ValueError):
            validate_comparison(comparison)
        comparison = json.loads(COMPARISON_FIXTURE.read_text(encoding="utf-8"))
        comparison["rules"]["ranking_claims_allowed"] = True
        with self.assertRaises(SchemaValidationError):
            validate_comparison(comparison)


if __name__ == "__main__":
    unittest.main()
