"""The local catalog must not expose downloads on stale or unrelated approvals."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_press_index
import test_art_policy


class PressIndexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.previous_root = build_press_index.ROOT
        build_press_index.ROOT = self.root
        self.addCleanup(setattr, build_press_index, 'ROOT', self.previous_root)
        self.addCleanup(self.temp.cleanup)
        for directory in ('schemas', 'art', 'brand/assets/identity', 'execution', 'config'):
            (self.root / directory).mkdir(parents=True)
        (self.root / 'schemas/approval.schema.json').write_bytes((ROOT / 'schemas/approval.schema.json').read_bytes())
        fixture = test_art_policy.ArtPolicyTests()
        fixture.setUp()
        self.addCleanup(fixture.tearDown)
        self.plan, self.record, self.asset = fixture.root_fixture()
        for name in ('prompt.md', 'master.png'):
            (self.root / name).write_bytes((fixture.root / name).read_bytes())
        self.path = 'master.png'
        self.sha = self.asset['exports'][0]['sha256']
        self.asset.update(approval_references=['execution/approval.json'], alt_text='Synthetic fixture')
        self.plan['title'] = 'Test asset'
        self.registry = [self.plan]
        self.manifest = [self.asset]
        self.approval = {'approval_id': 'synthetic-test-only', 'authority_reference': 'synthetic-test-only',
                         'approved_at': '2020-01-01T00:00:00Z', 'expires_at': None, 'operation': 'publish_asset',
                         'target': self.path, 'source_digest': self.sha, 'allowed_surfaces': ['press_kit'],
                         'allowed_fields': ['asset'], 'scope_notes': 'Synthetic test, no publication authority.', 'revoked': False}
        self.enrolled = True

    def render(self):
        (self.root / 'art/asset-registry.json').write_text(json.dumps(self.registry))
        (self.root / 'brand/asset-manifest.json').write_text(json.dumps(self.manifest))
        (self.root / 'execution/approval.json').write_text(json.dumps(self.approval))
        registration = {'approval_id': self.approval['approval_id'],
                        'authority_reference': self.approval['authority_reference'],
                        'approval_digest': build_press_index.approval_digest(self.approval)}
        (self.root / 'config/press-authorities.json').write_text(json.dumps({
            'schema_version': 'press-authorities-v1',
            'approvals': [registration] if self.enrolled else []}))
        with contextlib.redirect_stdout(io.StringIO()):
            build_press_index.main()
        return (self.root / 'brand/assets/press/index.html').read_text()

    def test_matching_record_permits_local_download_link(self):
        self.assertIn(' download>', self.render())

    def test_missing_approval_keeps_catalog_empty(self):
        self.asset['approval_references'] = []
        self.assertNotIn(' download>', self.render())

    def test_content_supplied_approval_cannot_enroll_itself(self):
        self.enrolled = False
        with self.assertRaisesRegex(ValueError, 'not enrolled'):
            self.render()

    def test_wrong_scope_digest_revocation_and_expiry_are_rejected(self):
        cases = [('target', 'different.png'), ('source_digest', '0' * 64),
                 ('operation', 'merge'), ('allowed_surfaces', ['website']), ('allowed_fields', ['caption']), ('revoked', True),
                 ('expires_at', '2020-01-02T00:00:00Z'), ('approved_at', '2999-01-01T00:00:00Z')]
        for key, value in cases:
            original = self.approval[key]
            with self.subTest(key=key):
                self.approval[key] = value
                self.assertNotIn(' download>', self.render())
            self.approval[key] = original

    def test_changed_export_bytes_are_rejected(self):
        (self.root / self.path).write_bytes(b'changed after review')
        with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
            self.render()

    def test_verified_label_cannot_bypass_missing_generation(self):
        self.asset['generation_records'] = []
        with self.assertRaisesRegex(ValueError, 'lineage rejected'):
            self.render()

    def test_changed_prompt_or_source_is_rejected(self):
        (self.root / 'prompt.md').write_text('Changed after generation review')
        with self.assertRaisesRegex(ValueError, 'lineage rejected'):
            self.render()

    def test_unrelated_pending_family_does_not_block_approved_family(self):
        self.registry.append({'id': 'UNRELATED', 'title': 'Unrelated', 'mandatory': True})
        self.manifest.append({'asset_id': 'UNRELATED', 'status': 'blocked'})
        self.assertIn(' download>', self.render())

    def test_shared_generation_validates_actual_parent_delivery(self):
        import copy
        parent = copy.deepcopy(self.asset)
        parent['approval_references'] = []
        self.asset['asset_id'] = 'CHILD'
        child_plan = copy.deepcopy(self.plan)
        child_plan.update(id='CHILD', parent_asset_ids=[self.plan['id']])
        self.registry.append(child_plan)
        self.manifest.append(parent)
        self.assertIn(' download>', self.render())
        parent['rights_status'] = 'unreviewed'
        with self.assertRaisesRegex(ValueError, 'Uncleared use'):
            self.render()


if __name__ == '__main__':
    unittest.main()
