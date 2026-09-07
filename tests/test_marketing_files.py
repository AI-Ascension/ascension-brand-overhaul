import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKETING = ROOT / "marketing"


class MarketingFileContractTests(unittest.TestCase):
    def test_required_directories_and_launch_assets_exist(self):
        for directory, count in (("episodes", 12), ("clips", 24), ("articles", 6)):
            files = sorted((MARKETING / directory).glob("*.md"))
            self.assertEqual(len(files), count, directory)
            self.assertTrue(all(path.stat().st_size > 400 for path in files))
        for name in (
            "README.md",
            "calendar.json",
            "asset-dependency.json",
            "source-map.json",
            "community-playbook.md",
            "experiments.json",
            "sponsorship.md",
        ):
            self.assertTrue((MARKETING / name).is_file(), name)
        for name in (
            "README.md",
            "first-episode.md",
            "launch-posts.md",
            "email-digest.md",
            "profile-and-press.md",
        ):
            self.assertTrue((MARKETING / "launch" / name).is_file(), name)

    def test_first_episode_has_both_script_forms_and_qualified_copy(self):
        text = (MARKETING / "launch/first-episode.md").read_text(encoding="utf-8")
        for phrase in (
            "actual-capture-ready",
            "report-only publication script",
            "Qualified copy variants",
            "Thumbnail copy variants",
            "Road to the First Verified Win",
            "333 settled operations",
            "431 settled operations",
            "No thumbnail or poster has been delivered",
        ):
            self.assertIn(phrase, text)

    def test_creator_and_community_boundaries_are_written(self):
        outreach = (MARKETING / "creator-kit/outreach-drafts.md").read_text(encoding="utf-8")
        community = (MARKETING / "community-playbook.md").read_text(encoding="utf-8")
        sponsorship = (MARKETING / "sponsorship.md").read_text(encoding="utf-8")
        for phrase in ("Slot A", "Slot B", "Slot C", "Slot D",
                       "Bounded request", "No payment", "No private"):
            self.assertIn(phrase, outreach)
        for phrase in ("Journey: spectator", "Journey: contributor",
                       "Journey: annotator", "Journey: challenge proposer",
                       "Journey: correction reporter", "Moderation rules"):
            self.assertIn(phrase, community)
        for phrase in ("Mandatory disclosure", "No ads", "Prohibited arrangements",
                       "favorable outcome"):
            self.assertIn(phrase, sponsorship)

