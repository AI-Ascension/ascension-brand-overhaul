import copy
import unittest

from publisher.canonical import source_digest
from publisher.errors import PublisherError, ProductionGateError
from publisher.validate import validate_manifest, validate_production_publication
from tests.test_publication import approved_fixture, load_fixture


class PublicationLineageTests(unittest.TestCase):
    def check_invalid(self, manifest):
        manifest['source']['content_digest'] = source_digest(manifest)
        with self.assertRaises(PublisherError):
            validate_manifest(manifest)

    def test_report_only_cannot_gain_invented_decisions(self):
        manifest, approval = approved_fixture()
        synthetic = load_fixture()
        manifest['action_timeline'] = synthetic['action_timeline']
        manifest['local_guess_reveal'] = synthetic['local_guess_reveal']
        manifest['source']['content_digest'] = source_digest(manifest)
        approval['source_digest'] = manifest['source']['content_digest']
        with self.assertRaisesRegex(ProductionGateError, 'report-only'):
            validate_production_publication(manifest, approval)

    def test_ambiguous_and_unlisted_source_references_fail(self):
        manifest = load_fixture()
        manifest['source']['references'].append(copy.deepcopy(manifest['source']['references'][0]))
        self.check_invalid(manifest)
        manifest = load_fixture()
        manifest['evidence_context']['source_reference'] = 'unlisted-source'
        self.check_invalid(manifest)
        manifest = load_fixture()
        manifest['action_timeline']['decisions'][0]['explanation']['source_reference'] = 'unlisted-source'
        self.check_invalid(manifest)

    def test_timing_and_guess_metadata_match_content(self):
        manifest = load_fixture()
        manifest['action_timeline']['decisions'][0]['timing']['captured'] = True
        self.check_invalid(manifest)
        manifest = load_fixture()
        manifest['local_guess_reveal']['legal_option_count'] = 3
        self.check_invalid(manifest)
        manifest, _ = approved_fixture()
        manifest['local_guess_reveal']['legal_option_count'] = 2
        self.check_invalid(manifest)

    def test_absent_optional_explanation_and_timing_remain_valid(self):
        manifest = load_fixture()
        manifest['action_timeline']['decisions'][0].update(explanation=None, timing=None)
        manifest['source']['content_digest'] = source_digest(manifest)
        validate_manifest(manifest)
