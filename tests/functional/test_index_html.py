import requests


class TestIndexHtml():
    def test_index_html_matches(self):
        """
        Tests whether the landing page is rendered and served correctly;
        just a form so no templating actually takes place
        """

        with open('./templates/index.html', 'r') as rf:
            template_content = rf.read()[:-1]  # TODO what is this final extra char?

        resp = requests.get('http://localhost:5000/')
        rendered_content = resp.text

        assert template_content == rendered_content
