"""Focused regression checks for the W02 functional token contract.

These checks cover the color pairs used by the shipped CSS primitives. They
are not a complete WCAG audit or a substitute for browser inspection.
"""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def luminance(value):
    channels = [int(value[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(first, second):
    one, two = luminance(first), luminance(second)
    return (max(one, two) + 0.05) / (min(one, two) + 0.05)


def css_values(css, variable):
    pattern = rf"(?m)^\s*{re.escape(variable)}\s*:\s*(#[0-9a-fA-F]{{6}})\s*;"
    return [value.lower() for value in re.findall(pattern, css)]


class BrandTokenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tokens = json.loads((ROOT / "brand/tokens.json").read_text(encoding="utf-8"))
        cls.css = (ROOT / "brand/tokens.css").read_text(encoding="utf-8")
        cls.access = json.loads((ROOT / "execution/w02-access.json").read_text(encoding="utf-8"))

    def test_declared_hex_values_are_well_formed(self):
        primitive = self.tokens["color"]["primitive"]
        for name, value in primitive.items():
            with self.subTest(name=name):
                self.assertRegex(value, HEX)

    def test_css_core_theme_values_match_json(self):
        mappings = {
            "surface.page": "--aa-color-surface-page",
            "surface.raised": "--aa-color-surface-raised",
            "surface.subtle": "--aa-color-surface-subtle",
            "text.primary": "--aa-color-text-primary",
            "text.secondary": "--aa-color-text-secondary",
            "border.default": "--aa-color-border-default",
            "border.strong": "--aa-color-border-strong",
            "accent.text": "--aa-color-accent-text",
            "accent.hover": "--aa-color-accent-hover",
            "focus": "--aa-color-focus",
        }
        for theme, position in (("light", 0), ("dark", -1)):
            values = self.tokens["color"]["theme"][theme]
            for path, variable in mappings.items():
                section, key = path.split(".") if "." in path else (None, path)
                expected = values[section][key] if section else values[key]
                observed = css_values(self.css, variable)
                with self.subTest(theme=theme, variable=variable):
                    self.assertGreaterEqual(len(observed), 2)
                    self.assertEqual(observed[position], expected.lower())

    def test_css_status_values_match_json(self):
        for name, status in self.tokens["color"]["status"].items():
            css_name = name.replace("sourceDerived", "source-derived")
            for theme in ("light", "dark"):
                for role in ("foreground", "background", "border"):
                    variable = f"--aa-status-{css_name}-{role}"
                    expected = status[theme][role].lower()
                    with self.subTest(status=name, theme=theme, role=role):
                        self.assertIn(expected, css_values(self.css, variable))

    def test_used_secondary_control_border_has_three_to_one_contrast(self):
        declaration = re.search(r"\.aa-button--secondary\s*\{([^}]*)\}", self.css, re.S)
        self.assertIsNotNone(declaration)
        self.assertIn("border-color: var(--aa-color-border-strong)", declaration.group(1))

        for theme, values in self.tokens["color"]["theme"].items():
            border = values["border"]["strong"]
            for surface_name, surface in values["surface"].items():
                if surface_name == "inverse":
                    continue
                with self.subTest(theme=theme, surface=surface_name):
                    self.assertGreaterEqual(contrast(border, surface), 3.0)

    def test_used_text_pairs_meet_targeted_contrast(self):
        for theme, values in self.tokens["color"]["theme"].items():
            with self.subTest(theme=theme, pair="body"):
                self.assertGreaterEqual(contrast(values["text"]["primary"], values["surface"]["page"]), 4.5)
            with self.subTest(theme=theme, pair="secondary"):
                self.assertGreaterEqual(contrast(values["text"]["secondary"], values["surface"]["page"]), 4.5)
            with self.subTest(theme=theme, pair="primary-button"):
                self.assertGreaterEqual(contrast(values["text"]["onAccent"], values["accent"]["text"]), 4.5)

            for name, status in self.tokens["color"]["status"].items():
                with self.subTest(theme=theme, status=name):
                    self.assertGreaterEqual(
                        contrast(status[theme]["foreground"], status[theme]["background"]), 4.5
                    )

    def test_art_gate_and_native_observation_remain_truthful(self):
        self.assertEqual(self.tokens["art"]["runtimeStatus"], "blocked")
        self.assertEqual(self.access["artStatus"]["blockedCount"], 72)
        self.assertEqual(len(self.access["artStatus"]["blockedIds"]), 72)
        self.assertEqual(self.access["artStatus"]["promptsAuthored"], 0)
        self.assertEqual(self.access["artStatus"]["rawOutputsPresent"], 0)
        self.assertEqual(self.access["artStatus"]["fallbackUsed"], False)

        nodes = {node["roleId"]: node for node in self.access["nativeLineage"]["nodes"]}
        lead = nodes["W02-L"]
        self.assertEqual(lead["observed"]["nativeAgentId"], "01a07a53-0521-7673-b4fd-15921bfaa4b8")
        self.assertEqual(lead["observed"]["parentNativeAgentId"], "01a07a4b-38ad-7673-b653-dad49eed9dbd")
        self.assertEqual(lead["observed"]["model"], "gpt-5.6-luna")
        self.assertEqual(lead["observed"]["reasoningEffort"], "max")
        self.assertEqual(nodes["W02-C1"]["status"], "blocked")
        self.assertEqual(nodes["W02-C1-BUILD"]["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
