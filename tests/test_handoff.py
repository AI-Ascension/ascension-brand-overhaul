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

    def test_blocked_requirement_needs_an_explicit_nonempty_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.fixture(root)
            path=root/'execution/requirements-status.json'
            data=json.loads(path.read_text())
            data['requirements'][0].update(status='blocked',blocker=' ',reason=None)
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'lacks a blocker or reason'):
                handoff.render(root)

    def release(self):
        return {'schema_version':'ai-ascension.release-status.v1', 'summary':'<script>unsafe</script>',
                'dimensions':{'local':'verified'}, 'verified_work':['source reviewed'],
                'remaining_conditions':['art blocked'], 'review_records':['review.json'],
                'unverified_assumptions':['no provider attestation']}

    def test_release_sections_escape_text_and_bind_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.fixture(root)
            (root/'execution/release-status.json').write_text(json.dumps(self.release()))
            report=handoff.render(root, require_release=True)
            self.assertIn('## Delivery scope', report)
            self.assertIn('&lt;script&gt;unsafe&lt;/script&gt;', report)
            self.assertNotIn('<script>', report)
            self.assertIn('execution/release-status.json |', report)
            self.assertIn('no provider attestation', report)

    def test_release_missing_wrong_empty_and_extra_shapes_fail(self):
        for mutation in ['missing','marker','summary','dimensions_list','dimensions_empty','array_string','array_empty','array_item','extra']:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp); self.fixture(root); data=self.release()
                if mutation=='missing': data.pop('summary')
                elif mutation=='marker': data['schema_version']='other'
                elif mutation=='summary': data['summary']=' '
                elif mutation=='dimensions_list': data['dimensions']=[]
                elif mutation=='dimensions_empty': data['dimensions']={}
                elif mutation=='array_string': data['verified_work']='oops'
                elif mutation=='array_empty': data['verified_work']=[]
                elif mutation=='array_item': data['verified_work']=[{}]
                else: data['unexpected']=True
                (root/'execution/release-status.json').write_text(json.dumps(data))
                with self.assertRaises(ValueError): handoff.render(root)

    def test_release_duplicate_keys_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.fixture(root)
            raw=json.dumps(self.release()).replace('{','{"summary":"duplicate",',1)
            (root/'execution/release-status.json').write_text(raw)
            with self.assertRaisesRegex(ValueError,'Duplicate ledger key'): handoff.render(root)

    def test_release_is_required_for_final_but_optional_for_legacy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.fixture(root)
            self.assertIn('Implementation handoff', handoff.render(root))
            with self.assertRaisesRegex(ValueError,'requires execution/release-status'): handoff.render(root,require_release=True)

    def test_release_directory_and_dangling_symlink_fail(self):
        for kind in ['directory','dangling']:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp); self.fixture(root); path=root/'execution/release-status.json'
                if kind=='directory': path.mkdir()
                else: path.symlink_to(root/'missing.json')
                with self.assertRaises(ValueError): handoff.render(root)

    def test_optional_source_digest_inputs_use_safe_bounded_json_reader(self):
        for kind in ['external_symlink','oversized','non_json','directory','dangling']:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
                root=Path(tmp); self.fixture(root); path=root/'execution/source-tree-inventory.json'
                if kind=='external_symlink':
                    target=Path(outside)/'source.json'; target.write_text('{}'); path.symlink_to(target)
                elif kind=='oversized': path.write_bytes(b' '*(4*1024*1024+1))
                elif kind=='non_json': path.write_text('not JSON')
                elif kind=='directory': path.mkdir()
                else: path.symlink_to(root/'missing.json')
                with self.assertRaises(ValueError): handoff.render(root)


if __name__ == '__main__':
    unittest.main()
