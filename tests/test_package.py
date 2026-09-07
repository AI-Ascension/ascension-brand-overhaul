import copy, importlib.util, json, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py')
    obj=importlib.util.module_from_spec(spec); spec.loader.exec_module(obj); return obj
vp=module('validate_package'); ledger=module('agent_ledger'); art=module('validate_assets'); archive=module('build_delivery')
def node(i,parent,depth,start,closed=None):
    return {'id':i,'parent_id':parent,'depth':depth,'role_id':{1:'W01-L',2:'W01-C1',3:'W01-C1-BUILD'}.get(depth,'W01-C1-BUILD'),'requested_model':'gpt-5.6-luna','requested_effort':'max','opened_at':f'2026-09-06T00:00:{start:02d}Z','closed_at':closed,'model_verified':False}
def chain():
    return {'root_id':'root','budget':12,'agents':[node('lead','root',1,1),node('coord','lead',2,2),node('leaf','coord',3,3)]}
class PackageTests(unittest.TestCase):
    def test_package_structure(self): self.assertEqual(vp.validate(ROOT),[])
    def test_native_depth_chain_record(self):
        r=ledger.validate_ledger(chain()); self.assertTrue(r['has_depth_three_chain']); self.assertEqual(r['peak_open_descendants'],3); self.assertFalse(r['all_models_verified'])
    def test_fourth_depth_rejected(self):
        c=chain(); c['agents'].append(node('illegal','leaf',4,4))
        with self.assertRaises(ValueError): ledger.validate_ledger(c)
    def test_wrong_model_rejected(self):
        c=chain(); c['agents'][2]['requested_model']='other'
        with self.assertRaises(ValueError): ledger.validate_ledger(c)
    def test_effort_substitution_rejected(self):
        c=chain(); c['agents'][2]['requested_effort']='xhigh'
        with self.assertRaises(ValueError): ledger.validate_ledger(c)
    def test_open_parents_count_toward_budget(self):
        c=chain(); c['budget']=2
        with self.assertRaises(ValueError): ledger.validate_ledger(c)
    def test_false_model_verification_rejected(self):
        c=chain(); c['agents'][2]['model_verified']=True
        with self.assertRaises(ValueError): ledger.validate_ledger(c)
    def test_parent_closed_too_early_rejected(self):
        c=chain(); c['agents'][0]['closed_at']='2026-09-06T00:00:04Z'
        with self.assertRaises(ValueError): ledger.validate_ledger(c)
    def test_closed_slots_reused(self):
        c={'root_id':'root','budget':1,'agents':[node('a','root',1,1,'2026-09-06T00:00:02Z'),node('b','root',1,2)]}
        self.assertEqual(ledger.validate_ledger(c)['peak_open_descendants'],1)
    def test_synthetic_fixture_is_not_public(self):
        fixture=json.loads((ROOT/'examples/public-run.synthetic.json').read_text())
        self.assertTrue(fixture['test_fixture']); self.assertEqual(fixture['classification'],'synthetic'); self.assertIsNone(fixture['approval_reference'])
    def test_empty_asset_delivery_rejected(self):
        reg=json.loads((ROOT/'art/asset-registry.json').read_text())
        self.assertTrue(art.verify(reg,[],ROOT))
    def test_svg_active_content_rejected(self):
        with self.assertRaises(ValueError): art.inspect_svg(b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>')
    def test_svg_external_reference_rejected(self):
        with self.assertRaises(ValueError): art.inspect_svg(b'<svg xmlns="http://www.w3.org/2000/svg"><image href="https://example.invalid/image.png"/></svg>')
    def test_legacy_svg_security_parse_allowed(self): art.inspect_svg(b'<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0L1 1"/></svg>')
    def test_path_traversal_rejected(self):
        with self.assertRaises(ValueError): art.checked_path(ROOT,'../private.txt')
    def test_archive_destination_safety(self):
        with self.assertRaises(ValueError): archive.build(ROOT,ROOT/'nested.zip')
    def test_archive_excludes_fonts_and_private_dirs(self):
        import zipfile
        with tempfile.TemporaryDirectory() as td:
            t=Path(td); s=t/'source'; s.mkdir(); (s/'public.md').write_text('safe'); (s/'font.woff2').write_bytes(b'font'); (s/'private').mkdir(); (s/'private'/'data.txt').write_text('private')
            archive.build(s,t/'out.zip')
            with zipfile.ZipFile(t/'out.zip') as z: self.assertEqual(z.namelist(),['source/public.md'])
if __name__=='__main__': unittest.main()
