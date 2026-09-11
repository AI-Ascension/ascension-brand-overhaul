"""Synthetic local consistency tests; none of these IDs claim actual native/provider execution."""
import copy
import hashlib
import importlib.util
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import art_policy
import agent_ledger
import validate_assets


def native_chain():
    roles = [('lead','root',1,'W02-L'),('coord','lead',2,'W02-C2'),('author','coord',3,'W02-C2-BUILD')]
    nodes=[]
    for ident,parent,depth,role in roles:
        model,effort=art_policy.expected_settings(role)
        n={'id':ident,'parent_id':parent,'depth':depth,'role_id':role,'opened_at':f'2026-09-07T00:00:0{depth}Z','closed_at':None,
           'model_verified':True,'runtime_evidence_reference':'synthetic-test-only-native-log'}
        for phase in ('requested','accepted','observed'):
            n[phase+'_model']=model;n[phase+'_effort']=effort
        nodes.append(n)
    return {'root_id':'root','budget':12,'agents':nodes}


class ArtPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.prompt=b'Synthetic test prompt, not an actual Astra-authored execution artifact.'
        self.png=b'\x89PNG\r\n\x1a\n'+b'\x00'*8+struct.pack('>II',64,64)
        (self.root/'prompt.md').write_bytes(self.prompt);(self.root/'master.png').write_bytes(self.png)
        self.planned={'id':'TEST-ART','mandatory':True,'method':'generate','prompt_author_role_id':'W02-C2-BUILD',
                      'exports':[{'path':'master.png','size':'64×64','format':'png','requires_generation_lineage':True}]}
        self.record={'record_id':'test-job','asset_id':'TEST-ART','status':'verified','test_fixture':False,
            'author_role_id':'W02-C2-BUILD','author_agent_id':'author','author_parent_id':'coord','author_depth':3,
            'author_runtime_evidence_reference':'synthetic-test-only-native-log','prompt_path':'prompt.md',
            'prompt_sha256':hashlib.sha256(self.prompt).hexdigest(),'image_model_requested':'gpt-image-2',
            'image_model_observed':'gpt-image-2','image_model_evidence_reference':'synthetic-test-only-image-log',
            'snapshot_alias_evidence_reference':None,'tool_name':'synthetic-test-only','tool_execution_reference':'synthetic-test-only-image-call',
            'reviewer_reference':'synthetic-test-only-independent-review','created_at':'2026-09-07T00:00:04Z',
            'reference_inputs':[],'raw_outputs':[{'path':'master.png','sha256':hashlib.sha256(self.png).hexdigest(),'format':'png','width':64,'height':64}]}
        for phase in ('requested','accepted','observed'):
            self.record[phase+'_author_model']='gpt-6-astra';self.record[phase+'_author_effort']='max'
        self.ledger=native_chain()
        self.manifest={'asset_id':'TEST-ART','status':'verified','method':'generate','origin':'astra_authored_gpt_image_2',
            'reviewer_reference':'synthetic-test-only-independent-review','rights_status':'generated_original_reviewed',
            'source_references':['synthetic-test-only'],'generation_records':[self.record],
            'exports':[{'path':'master.png','sha256':hashlib.sha256(self.png).hexdigest(),'format':'png','width':64,'height':64,
                        'generation_record_id':'test-job','raw_source_path':'master.png','derivation_operations':['identity']}]}
    def tearDown(self): self.temp.cleanup()
    def errors(self): return art_policy.validate_generation_record(self.record,self.planned,self.root,self.ledger)
    def test_declared_art_policy_consistency(self): self.assertEqual(self.errors(),[])
    def root_fixture(self):
        planned=copy.deepcopy(self.planned)
        planned['prompt_author_role_id']='ROOT'
        record=copy.deepcopy(self.record)
        record.update(generation_route=art_policy.ROOT_ROUTE, author_role_id='ROOT', author_agent_id='root',
                      author_parent_id=None, author_depth=0, image_model_requested='unknown',
                      image_model_observed='unknown', image_backend='unspecified',
                      tool_name='image_gen__imagegen',
                      author_runtime_evidence_reference='not-applicable:user-authorized-root-route',
                      image_model_evidence_reference='not-observed:available-image-tool',
                      user_authorization_reference=art_policy.ROOT_AUTHORIZATION_PATH,
                      user_authorization_sha256=art_policy.ROOT_AUTHORIZATION['sha256'])
        for phase in ('requested','accepted','observed'):
            record[phase+'_author_model']='unknown';record[phase+'_author_effort']='unknown'
        manifest=copy.deepcopy(self.manifest)
        manifest.update(generation_route=art_policy.ROOT_ROUTE, origin='root_user_authorized_image_tool',
                        generation_records=[record])
        return planned,record,manifest

    def test_authorized_root_route_accepts_without_native_ledger(self):
        planned,record,manifest=self.root_fixture()
        self.assertEqual(art_policy.validate_generation_record(record,planned,self.root,None),[])
        self.assertEqual(validate_assets.verify([planned],[manifest],self.root,None),[])
        self.assertEqual(validate_assets.verify([planned],[manifest],self.root,{'not':'a native ledger'}),[])

    def test_root_route_requires_canonical_user_authorization(self):
        planned,record,_=self.root_fixture()
        record['user_authorization_reference']='art/fake-authorization.json'
        self.assertTrue(art_policy.validate_generation_record(record,planned,self.root,None))
        record['user_authorization_reference']=art_policy.ROOT_AUTHORIZATION_PATH
        record['user_authorization_sha256']='0'*64
        self.assertTrue(art_policy.validate_generation_record(record,planned,self.root,None))

    def test_root_route_requires_explicit_null_parent(self):
        planned,record,_=self.root_fixture()
        del record['author_parent_id']
        self.assertTrue(art_policy.validate_generation_record(record,planned,self.root,None))

    def test_root_route_rejects_spoofed_model_or_backend(self):
        planned,record,_=self.root_fixture()
        for field,value in [('image_model_requested','gpt-image-2'),('image_model_observed','gpt-image-2'),
                            ('image_backend','openai'),('requested_author_model','gpt-6-astra')]:
            candidate=copy.deepcopy(record);candidate[field]=value
            with self.subTest(field=field): self.assertTrue(art_policy.validate_generation_record(candidate,planned,self.root,None))

    def test_root_route_asset_origin_is_checked(self):
        planned,_,manifest=self.root_fixture()
        self.assertEqual(validate_assets.verify([planned],[manifest],self.root,None),[])
        manifest['origin']='astra_authored_gpt_image_2'
        self.assertTrue(validate_assets.verify([planned],[manifest],self.root,None))

    def test_explicit_legacy_route_remains_valid(self):
        self.record['generation_route']=art_policy.LEGACY_ROUTE
        self.assertEqual(self.errors(),[])
    def test_designated_astra_native_chain(self):
        result=agent_ledger.validate_ledger(self.ledger);self.assertEqual(result['astra_author_nodes'],1);self.assertTrue(result['all_models_verified'])
    def test_ordinary_role_cannot_become_astra(self):
        self.ledger['agents'][0]['requested_model']='gpt-6-astra'
        with self.assertRaises(ValueError):agent_ledger.validate_ledger(self.ledger)
    def test_astra_role_cannot_fall_back_to_luna(self):
        self.ledger['agents'][2]['requested_model']='gpt-5.6-luna'
        with self.assertRaises(ValueError):agent_ledger.validate_ledger(self.ledger)
    def test_wrong_native_parent_role_rejected(self):
        self.ledger['agents'][0]['role_id']='W01-L'
        with self.assertRaises(ValueError):agent_ledger.validate_ledger(self.ledger)
    def test_wrong_prompt_author_rejected(self):
        self.record['observed_author_model']='gpt-5.6-luna';self.assertTrue(self.errors())
    def test_wrong_image_model_rejected(self):
        self.record['image_model_requested']='gpt-image-1.5';self.assertTrue(self.errors())
    def test_unknown_backend_rejected(self):
        self.record['image_model_observed']=None;self.assertTrue(self.errors())
    def test_documented_snapshot_needs_alias_evidence(self):
        self.record['image_model_observed']='gpt-image-2-2026-04-21';self.assertTrue(self.errors())
        self.record['snapshot_alias_evidence_reference']='synthetic-test-only-alias-proof';self.assertTrue(self.errors())
        alias={'schema_version':'image-model-alias-v1','requested_model':'gpt-image-2','resolved_model':'gpt-image-2-2026-04-21','source_reference':'https://developers.openai.com/synthetic-test-only','captured_at':'2026-09-07T00:00:00Z','reviewer_reference':'synthetic-test-only-review'}
        raw=json.dumps(alias).encode();(self.root/'alias.json').write_bytes(raw)
        self.record.update(snapshot_alias_evidence_reference='alias.json',snapshot_alias_evidence_sha256=hashlib.sha256(raw).hexdigest())
        self.assertEqual(self.errors(),[])
        (self.root/'alias.json').write_text('{}');self.assertTrue(self.errors())
    def test_model_verification_string_is_not_a_boolean(self):
        for value in ['false', 'true', 1, None]:
            self.ledger['agents'][0]['model_verified']=value
            with self.subTest(value=value), self.assertRaises(ValueError):agent_ledger.validate_ledger(self.ledger)
    def test_unplanned_and_case_colliding_exports_are_rejected(self):
        for name in ['extra.png', 'MASTER.png']:
            manifest=copy.deepcopy(self.manifest)
            manifest['exports'].append({**manifest['exports'][0],'path':name})
            self.assertTrue(validate_assets.verify([self.planned],[manifest],self.root,self.ledger))
    def test_unverified_native_astra_rejected(self):
        self.ledger['agents'][2]['model_verified']=False;self.assertTrue(self.errors())
    def test_missing_native_ledger_rejected(self):
        self.assertTrue(art_policy.validate_generation_record(self.record,self.planned,self.root,None))
    def test_prompt_hash_tamper_rejected(self):
        (self.root/'prompt.md').write_text('changed');self.assertTrue(self.errors())
    def test_missing_original_generation_rejected(self):
        self.record['raw_outputs']=[];self.assertTrue(self.errors())
    def test_synthetic_generation_not_publishable(self):
        self.record['test_fixture']=True;self.assertTrue(self.errors())
    def test_author_cannot_self_approve(self):
        self.record['reviewer_reference']='author';self.assertTrue(self.errors())
    def test_native_vector_claim_rejected(self):
        self.record['raw_outputs'][0]['format']='svg';self.assertTrue(self.errors())
    def test_mechanical_export_allowed(self):
        self.assertEqual(validate_assets.verify([self.planned],[self.manifest],self.root,self.ledger),[])
    def test_code_drawn_asset_rejected(self):
        self.manifest['method']='vector';self.assertTrue(validate_assets.verify([self.planned],[self.manifest],self.root,self.ledger))
    def test_repaint_postprocess_rejected(self):
        self.manifest['exports'][0]['derivation_operations']=['repaint_text'];self.assertTrue(validate_assets.verify([self.planned],[self.manifest],self.root,self.ledger))
    def test_missing_export_generation_link_rejected(self):
        self.manifest['exports'][0]['generation_record_id']='missing';self.assertTrue(validate_assets.verify([self.planned],[self.manifest],self.root,self.ledger))
    def test_tool_prompt_rewrite_requires_astra_review(self):
        (self.root/'revised.md').write_bytes(self.prompt)
        self.record['provider_revised_prompt_path']='revised.md';self.record['provider_revised_prompt_sha256']=hashlib.sha256(self.prompt).hexdigest()
        self.assertTrue(self.errors());self.record['revised_prompt_astra_review_reference']='synthetic-test-only-astra-review';self.assertEqual(self.errors(),[])
    def test_all_art_rows_use_mandated_pipeline(self):
        rows=json.loads((ROOT/'art/asset-registry.json').read_text());self.assertEqual(len(rows),72)
        for asset in rows:
            route=asset.get('generation_route',art_policy.LEGACY_ROUTE)
            with self.subTest(asset=asset['id']):
                self.assertIn(route,art_policy.ROUTES)
                if route==art_policy.ROOT_ROUTE:
                    self.assertEqual(asset['method'],'generate')
                    self.assertEqual(asset['prompt_author_role_id'],'ROOT')
                    self.assertEqual(asset['prompt_author_model'],'unknown')
                    self.assertEqual(asset['generation_model'],'unknown')
                else:
                    self.assertEqual(asset['method'],'generate')
                    self.assertIn(asset['prompt_author_role_id'],art_policy.ART_ROLES)
                    self.assertEqual(asset['prompt_author_model'],'gpt-6-astra')
                    self.assertEqual(asset['generation_model'],'gpt-image-2')
    def root_parent_fixture(self):
        parent, record, delivered = self.root_fixture()
        child = copy.deepcopy(parent)
        child.update(id='CHILD', parent_asset_ids=[parent['id']])
        child['exports'][0]['path'] = 'child.png'
        child_delivery = copy.deepcopy(delivered)
        child_delivery['asset_id'] = 'CHILD'
        child_delivery['exports'][0]['path'] = 'child.png'
        (self.root/'child.png').write_bytes(self.png)
        return [parent, child], [delivered, child_delivery]

    def test_root_derivative_reuses_actual_parent_generation(self):
        registry, manifest = self.root_parent_fixture()
        self.assertEqual(validate_assets.verify(registry, manifest, self.root), [])
        self.assertEqual(manifest[1]['generation_records'], manifest[0]['generation_records'])

    def test_shared_generation_requires_declared_parent(self):
        registry, manifest = self.root_parent_fixture()
        registry[1]['parent_asset_ids'] = []
        self.assertTrue(validate_assets.verify(registry, manifest, self.root))

    def test_shared_generation_requires_verified_parent(self):
        registry, manifest = self.root_parent_fixture()
        manifest[0]['status'] = 'in_progress'
        self.assertTrue(validate_assets.verify(registry, manifest, self.root))

    def test_shared_generation_cannot_rewrite_parent_call(self):
        registry, manifest = self.root_parent_fixture()
        manifest[1]['generation_records'][0]['tool_execution_reference'] = 'invented-second-call'
        self.assertTrue(validate_assets.verify(registry, manifest, self.root))

    def test_reference_input_hash_is_checked(self):
        self.record['reference_inputs'] = [{'reference': 'master.png',
            'sha256': hashlib.sha256(self.png).hexdigest(),
            'rights_reference': 'synthetic-test-only-independent-source-review'}]
        self.assertEqual(self.errors(), [])
        self.record['reference_inputs'][0]['sha256'] = '0' * 64
        self.assertTrue(self.errors())

    def test_pending_reference_use_review_is_rejected(self):
        self.record['reference_inputs'] = [{'reference': 'master.png',
            'sha256': hashlib.sha256(self.png).hexdigest(),
            'rights_reference': 'pending:source-review'}]
        self.assertTrue(self.errors())

    def test_evidence_is_not_regenerated(self):
        rows=json.loads((ROOT/'art/evidence-media-registry.json').read_text());self.assertEqual(len(rows),3);self.assertTrue(all(a['generation_prohibited'] for a in rows))
    def test_legacy_is_not_new_brand_art(self):
        rows=json.loads((ROOT/'art/reference-registry.json').read_text());self.assertEqual(len(rows),5);self.assertTrue(all(a['allowed_on_new_brand_surfaces'] is False for a in rows))

if __name__=='__main__':unittest.main()
