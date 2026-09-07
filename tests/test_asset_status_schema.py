import copy
import importlib.util
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validate_assets', ROOT / 'scripts/validate_assets.py')
assets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assets)


def blocked_entry():
    row = copy.deepcopy(json.loads((ROOT / 'brand/asset-manifest.json').read_text())[0])
    row.update(status='blocked', generation_records=[], exports=[], blocker='Synthetic missing-access test case')
    return row


class AssetStatusSchemaTests(unittest.TestCase):
    def test_absent_art_is_recorded_without_invented_generations(self):
        schema = json.loads((ROOT / 'schemas/asset.schema.json').read_text())
        validator = Draft202012Validator(schema)
        manifest = json.loads((ROOT / 'brand/asset-manifest.json').read_text())
        registry = json.loads((ROOT / 'art/asset-registry.json').read_text())
        self.assertEqual({row['asset_id'] for row in manifest}, {row['id'] for row in registry})
        row = blocked_entry()
        validator.validate(row)
        errors = assets.verify([item for item in registry if item['id'] == row['asset_id']], [row], ROOT)
        self.assertEqual(len(errors), 1)
        self.assertTrue(all(message.startswith('Not verified: ') for message in errors))

    def test_empty_status_record_cannot_claim_verified(self):
        schema = json.loads((ROOT / 'schemas/asset.schema.json').read_text())
        validator = Draft202012Validator(schema)
        row = blocked_entry()
        row['status'] = 'verified'
        row['blocker'] = None
        errors = list(validator.iter_errors(row))
        self.assertIn(['generation_records'], [list(error.path) for error in errors])
        self.assertIn(['exports'], [list(error.path) for error in errors])
