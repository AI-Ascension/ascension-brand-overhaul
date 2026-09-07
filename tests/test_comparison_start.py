import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from publisher.comparison import validate_comparison
from tests.test_measurement import COMPARISON_FIXTURE


class ComparisonStartTests(unittest.TestCase):
    def comparison(self):
        comparison = json.loads(COMPARISON_FIXTURE.read_text())
        comparison['comparison_kind'] = 'same_start'
        comparison['rules']['same_start_required'] = True
        return comparison

    def test_flag_alone_cannot_establish_same_start(self):
        with self.assertRaisesRegex(ValueError, 'require source-owned'):
            validate_comparison(self.comparison())
        with tempfile.TemporaryDirectory() as temp, self.assertRaisesRegex(ValueError, 'missing start evidence'):
            validate_comparison(self.comparison(), start_evidence_root=temp)

    def test_files_bind_seed_state_and_build_and_reject_changed_bytes(self):
        comparison = self.comparison()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            record = {'schema_version': 'comparison-start-v1', 'game_build': 'fixture-build', 'seed_digest': 'a' * 64, 'initial_state_digest': 'b' * 64, 'source_reference': 'https://example.invalid/synthetic-start'}
            def write(index, content):
                raw = json.dumps(content).encode()
                (root / f'start-{index}.json').write_bytes(raw)
                comparison['runs'][index]['start_evidence'] = {'artifact_path': f'start-{index}.json', 'artifact_digest': hashlib.sha256(raw).hexdigest()}
            write(0, record)
            write(1, record)
            validate_comparison(comparison, start_evidence_root=root)
            (root / 'start-1.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'digest'):
                validate_comparison(comparison, start_evidence_root=root)
            write(1, dict(record, initial_state_digest='c' * 64))
            with self.assertRaisesRegex(ValueError, 'identities differ'):
                validate_comparison(comparison, start_evidence_root=root)
            write(1, dict(record, game_build='other-build'))
            with self.assertRaisesRegex(ValueError, 'game build differs'):
                validate_comparison(comparison, start_evidence_root=root)
