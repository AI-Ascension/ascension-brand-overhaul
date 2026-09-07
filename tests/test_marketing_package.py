import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
MARKETING = ROOT / "marketing"


class MarketingCalendarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calendar = json.loads((MARKETING / "calendar.json").read_text(encoding="utf-8"))
        cls.registry = json.loads((ROOT / "art/asset-registry.json").read_text(encoding="utf-8"))
        cls.registry_ids = {row["id"] for row in cls.registry}

    def test_required_counts_and_relative_schedule(self):
        self.assertEqual(self.calendar["integrity"]["item_counts"], {
            "episodes": 12, "clips": 24, "articles": 6
        })
        self.assertEqual(self.calendar["schedule"]["type"],
                         "relative_weeks_until_approved_launch_date")
        self.assertIsNone(self.calendar["schedule"]["launch_date"])
        self.assertEqual(self.calendar["schedule"]["operation_state"], "planning_only")

    def test_episode_week_and_distinctness(self):
        episodes = self.calendar["episodes"]
        self.assertEqual([item["week"] for item in episodes], list(range(1, 13)))
        self.assertEqual(len({item["title"] for item in episodes}), 12)
        self.assertEqual(len({item["truthful_hook"] for item in episodes}), 12)
        for item in episodes:
            self._assert_item(item, "episode_id")
        self.assertEqual(sorted({item["week"] for item in self.calendar["clips"]}),
                         list(range(1, 13)))
        per_week = {week: 0 for week in range(1, 13)}
        for item in self.calendar["clips"]:
            per_week[item["week"]] += 1
            self._assert_item(item, "clip_id")
        self.assertEqual(per_week, {week: 2 for week in range(1, 13)})
        self.assertEqual(len({item["title"] for item in self.calendar["clips"]}), 24)
        self.assertEqual(len({item["truthful_hook"] for item in self.calendar["clips"]}), 24)
        for item in self.calendar["articles"]:
            self._assert_item(item, "article_id")
        self.assertEqual(len({item["title"] for item in self.calendar["articles"]}), 6)

    def _assert_item(self, item, id_key):
        required = {
            id_key, "audience", "objective", "truthful_hook", "source_requirements",
            "asset_ids", "asset_records", "storyboard" if id_key != "article_id" else "outline",
            "cta", "destinations", "rights_approval", "owner", "measurement"
        }
        self.assertTrue(required.issubset(item), f"{id_key} missing fields")
        self.assertTrue(item["audience"] and item["objective"] and item["truthful_hook"])
        self.assertTrue(item["cta"] and item["owner"])
        self.assertGreater(len(item["source_requirements"]), 0)
        self.assertGreater(len(item["asset_ids"]), 0)
        self.assertEqual({row["asset_id"] for row in item["asset_records"]},
                         set(item["asset_ids"]))
        for asset_id in item["asset_ids"]:
            self.assertIn(asset_id, self.registry_ids, asset_id)
        for source in item["source_requirements"]:
            self.assertIn("source_id", source)
            self.assertIn("evidence_kind", source)
            self.assertIn("required_before_publish", source)
            if source["source_url"] is not None:
                parsed = urlparse(source["source_url"])
                self.assertIn(parsed.scheme, {"http", "https"})
                self.assertTrue(parsed.netloc)
            if source["evidence_kind"] == "required_future_public_artifact":
                self.assertIsNone(source["source_revision"])
        for destination in item["destinations"]:
            self.assertIn(destination["status"], {
                "real_public_report", "real_public_replay", "real_public_source",
                "real_source_repository", "planned_local_destination"
            })
            parsed = urlparse(destination["url"])
            self.assertIn(parsed.scheme, {"http", "https"})
            self.assertTrue(parsed.netloc)
            self.assertTrue(destination["gate"])
        approval = item["rights_approval"]
        self.assertEqual(approval["status"], "draft_only")
        self.assertFalse(approval["send_or_publish_authorized"])
        self.assertGreaterEqual(len(approval["required_reviewers"]), 2)
        measurement = item["measurement"]
        for key in ("primary_event", "numerator", "denominator", "window",
                    "bot_and_test_filter", "attribution_limit", "stop_rule",
                    "result_status", "privacy"):
            self.assertIn(key, measurement)
        self.assertEqual(measurement["result_status"], "unobserved")
        for record in item["asset_records"]:
            self.assertEqual(record["availability"], "blocked")
            self.assertEqual(record["status"], "planned")
            self.assertFalse(record["fallback_used"])

    def test_registry_dependency_record_covers_all_art_assets(self):
        dependency = json.loads((MARKETING / "asset-dependency.json").read_text(encoding="utf-8"))
        self.assertEqual(dependency["registry_count"], 72)
        self.assertEqual(len(dependency["assets"]), 72)
        self.assertEqual({row["asset_id"] for row in dependency["assets"]},
                         self.registry_ids)
        self.assertEqual(dependency["status"], "blocked")
        self.assertFalse(dependency["native_lineage"]["fallback_used"])
        for row in dependency["assets"]:
            self.assertEqual(row["availability"], "blocked")
            self.assertEqual(row["delivery_status"], "not_delivered")
            self.assertEqual(row["generation_status"], "not_attempted")
            self.assertEqual(row["rights_status"], "unreviewed")

    def test_no_campaign_operation_or_fake_result(self):
        text = "\n".join(path.read_text(encoding="utf-8")
                          for path in MARKETING.rglob("*") if path.is_file())
        self.assertNotIn("result_status: observed", text.lower())
        self.assertNotIn("campaign operated", text.lower())
        self.assertNotIn("audience result: 0", text.lower())
        self.assertNotRegex(text, r"(?i)\bwe (?:won|have won|achieved)\b")
