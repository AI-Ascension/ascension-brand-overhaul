from html.parser import HTMLParser
import json
from pathlib import Path
import unittest

from publisher.render import render_html


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.closed_details = []
        self.visible = []

    def handle_starttag(self, tag, attrs):
        if tag == 'details':
            self.closed_details.append('open' not in dict(attrs))

    def handle_endtag(self, tag):
        if tag == 'details':
            self.closed_details.pop()

    def handle_data(self, data):
        if not any(self.closed_details):
            self.visible.append(data)


class RenderBehavior(unittest.TestCase):
    def test_timeline_does_not_spoil_guess_consequence(self):
        fixture = Path(__file__).parent / 'fixtures/publication/run.synthetic.json'
        manifest = json.loads(fixture.read_text())
        page = render_html(manifest)
        parser = VisibleText()
        parser.feed(page)
        consequence = manifest['action_timeline']['decisions'][0]['observed_consequence']
        self.assertIn(consequence, page)
        self.assertNotIn(consequence, ''.join(parser.visible))
        explanation = manifest['action_timeline']['decisions'][0]['explanation']['text']
        self.assertNotIn(explanation, ''.join(parser.visible))


if __name__ == '__main__':
    unittest.main()
