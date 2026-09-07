import unittest

from publisher.canonical import source_digest
from publisher.errors import ApprovalError
from publisher.security import require_approved_text_uris
from publisher.validate import validate_production_publication
from tests.publication_authority_helper import trusted_registry
from tests.test_publication import approved_fixture


class PublicationUriSchemeTests(unittest.TestCase):
    def test_opaque_scheme_disclosures_cannot_be_emitted(self):
        for uri in ['mailto:private@example.invalid', 'data:text/plain,PRIVATE', 'javascript:private', 'urn:secret', 'file:/private']:
            with self.subTest(uri=uri):
                manifest, approval = approved_fixture()
                manifest['disclosures'].append('Unreviewed reference ' + uri)
                manifest['source']['content_digest'] = source_digest(manifest)
                approval['source_digest'] = manifest['source']['content_digest']
                with trusted_registry(approval), self.assertRaisesRegex(ApprovalError, 'URL-like text'):
                    validate_production_publication(manifest, approval)

    def test_prose_colons_and_approved_parenthesized_links_are_distinct(self):
        require_approved_text_uris({'claim': 'Result: Defeat (https://example.test/report).'}, ['https://example.test/report'])
        with self.assertRaises(ApprovalError):
            require_approved_text_uris('Result: https://example.test/private', ['https://example.test/report'])
