import html5lib
import requests


class TestIndexHtml():
    def test_index_html_matches(self):
        """
        Tests whether the landing page is rendered, validates html
        """
        resp = requests.get('http://localhost:5000/')
        rendered_content = resp.text
        parser = html5lib.HTMLParser(strict=True)
        assert parser.parse(rendered_content), "index template renders to valid html"
