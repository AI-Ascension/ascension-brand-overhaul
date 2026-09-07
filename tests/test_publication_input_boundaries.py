import json
from pathlib import Path
import tempfile
import unittest

from publisher import OfflinePublisher
from publisher.errors import PublisherError, SecurityError
from publisher.publisher import MAX_INPUT_BYTES


class PublicationInputBoundaries(unittest.TestCase):
    def test_symlink_output_is_rejected_before_resolution(self):
        fixture = Path(__file__).parent / 'fixtures/publication/run.synthetic.json'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            destination = root / 'destination'
            destination.mkdir()
            link = root / 'link'
            link.symlink_to(destination, target_is_directory=True)
            for method in ['render', 'publish']:
                with self.subTest(method=method), self.assertRaises(SecurityError):
                    if method == 'render':
                        OfflinePublisher().render(fixture, link / 'output')
                    else:
                        OfflinePublisher().publish(fixture, root / 'absent-approval.json', link / 'output')
            self.assertEqual(list(destination.iterdir()), [])

    def test_bounded_input_and_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'input.json'
            path.write_bytes(b' ' * (MAX_INPUT_BYTES + 1))
            with self.assertRaisesRegex(PublisherError, '4 MiB'):
                OfflinePublisher().ingest(path)
            path.write_text('{"classification":"private","classification":"approved_public"}')
            with self.assertRaisesRegex(PublisherError, 'duplicate'):
                OfflinePublisher().ingest(path)


if __name__ == '__main__':
    unittest.main()
