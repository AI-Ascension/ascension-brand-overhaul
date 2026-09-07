import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MarketingExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "marketing/experiments.json").read_text(encoding="utf-8"))

    def test_at_least_six_bounded_experiments(self):
        experiments = self.data["experiments"]
        self.assertGreaterEqual(len(experiments), 6)
        self.assertEqual(len({item["experiment_id"] for item in experiments}), len(experiments))
        for item in experiments:
            for key in (
                "experiment_id", "name", "hypothesis", "audience", "variants",
                "primary_metric", "observation_window", "stop_rule",
                "minimum_sample_or_qualitative_protocol", "confounders",
                "privacy", "attribution_limit", "result"
            ):
                self.assertIn(key, item, item.get("experiment_id"))
            metric = item["primary_metric"]
            self.assertIn("event_name", metric)
            self.assertTrue(metric["numerator"])
            self.assertTrue(metric["denominator"])
            self.assertTrue(metric["exclusion_rules"])
            result = item["result"]
            self.assertEqual(result["status"], "unobserved")
            self.assertIsNone(result["eligible_numerator"])
            self.assertIsNone(result["eligible_denominator"])
            self.assertEqual(result["notes"], [])
            self.assertIn("privacy", item)
            self.assertNotIn("@", json.dumps(item))

    def test_only_approved_event_vocabulary_is_used(self):
        allowed = {
            "run_page_view", "media_start", "meaningful_watch_or_read",
            "decision_presented", "decision_guess", "decision_reveal",
            "evidence_open", "replay_download", "build_start", "quickstart_success",
            "docs_error", "subscribe_confirmed", "unsubscribe_completed",
            "return_visit_proxy", "contributor_repeat_proxy", "correction_open"
        }
        for item in self.data["experiments"]:
            names = {item["primary_metric"]["event_name"], *item["secondary_metrics"]}
            self.assertTrue(names <= allowed, (item["experiment_id"], names - allowed))

