import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from publisher import OfflinePublisher, DuplicatePublicationError
from publisher.schema import unique_schema_object
from publisher.errors import SchemaValidationError

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/publication/run.synthetic.json'


class ReviewRepairs(unittest.TestCase):
    def test_all_schema_files_have_unambiguous_object_keys(self):
        for path in (ROOT / 'schemas').glob('*.json'):
            with self.subTest(schema=path.name):
                json.loads(path.read_text(), object_pairs_hook=unique_schema_object)
        with self.assertRaises(SchemaValidationError):
            json.loads('{"properties":{},"properties":{}}', object_pairs_hook=unique_schema_object)

    def test_failed_page_write_leaves_retryable_destination(self):
        original = Path.open
        def fail_page(path, *args, **kwargs):
            if path.name == 'index.html' and args and args[0] == 'xb':
                raise OSError('simulated full disk during page write')
            return original(path, *args, **kwargs)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            with patch.object(Path, 'open', fail_page), self.assertRaises(OSError):
                OfflinePublisher().render(FIXTURE, output)
            self.assertEqual(list(output.rglob('manifest.json')), [])
            self.assertEqual(list(output.rglob('.publication-*')), [])
            result = OfflinePublisher().render(FIXTURE, output)
            self.assertTrue(result.html_path.is_file())

    def test_idempotent_output_rejects_unexpected_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            result = OfflinePublisher().render(FIXTURE, output)
            extra = result.output_directory / 'secret.txt'
            extra.write_text('unrelated local content')
            with self.assertRaises(DuplicatePublicationError):
                OfflinePublisher().render(FIXTURE, output)
            self.assertEqual(extra.read_text(), 'unrelated local content')


if __name__ == '__main__':
    unittest.main()
