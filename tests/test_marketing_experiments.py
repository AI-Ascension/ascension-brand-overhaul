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
        contract = json.loads((ROOT / 'analytics/event-contract.json').read_text())
        schema = json.loads((ROOT / 'schemas/event.schema.json').read_text())
        events = {row['name'] for row in contract['events']}
        self.assertEqual(events, set(schema['properties']['event_name']['enum']))
        metrics = {row['id']: row for row in contract['metrics']}
        mappings = self.data['derived_metric_references']
        for item in self.data["experiments"]:
            self.assertIn(item['primary_metric']['event_name'], events)
            for name in item['secondary_metrics']:
                self.assertTrue(name in events or name in mappings, (item['experiment_id'], name))
        for name, mapping in mappings.items():
            self.assertIn(name, metrics)
            self.assertEqual(mapping['metric_id'], name)
            self.assertEqual(mapping['contract_path'], 'analytics/event-contract.json')
            self.assertEqual(set(mapping['source_events']), events)
            for key in ('numerator', 'denominator', 'window', 'exclusions', 'absent_value'):
                self.assertEqual(mapping[key], metrics[name][key])
            for key in ('consent', 'scope', 'interpretation_limit'):
                self.assertTrue(mapping[key])
