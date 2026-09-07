import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('handoff', ROOT / 'scripts/render_handoff.py')
handoff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handoff)


class HandoffTests(unittest.TestCase):
    def fixture(self, root):
        for name in ['data/requirements.json', 'execution/requirements-status.json', 'art/asset-registry.json', 'brand/asset-manifest.json', 'execution/operations.json']:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / name).read_bytes())

    def test_complete_inventory_and_determinism(self):
        report = handoff.render(ROOT)
        self.assertEqual(report, handoff.render(ROOT))
        for row in json.loads((ROOT / 'data/requirements.json').read_text()):
            self.assertIn('| ' + row['id'] + ' |', report)
        for row in json.loads((ROOT / 'art/asset-registry.json').read_text()):
            self.assertIn('| ' + row['id'] + ' |', report)
        self.assertIn('not an independent completion verdict', report)

    def test_missing_requirement_and_unsupported_verification_fail(self):
        for mutation in ['missing', 'unsupported', 'changed']:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.fixture(root)
                path = root / 'execution/requirements-status.json'
                data = json.loads(path.read_text())
                if mutation == 'missing':
                    data['requirements'].pop()
                elif mutation == 'unsupported':
                    data['requirements'][0].update(status='verified', verification_records=[], independent_reviewer=None)
                else:
                    data['requirements'][0]['requirement'] = 'Easier replacement objective'
                path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    handoff.render(root)


if __name__ == '__main__':
    unittest.main()
