import requests


class TestAnsifyUrl():
    def test_ansify_url(self):
        """
        Tests whether the /ansify endpoint produces expected output for a sample url
        """

        with open('./tests/static/test_ansify_url_expected.txt', 'r') as rf:
            expected = rf.read()

        resp = requests.post(
            'http://localhost:5000/ansify',
            data={'url': 'https://cdn.outsideonline.com/wp-content/uploads/2023/03/Funny_Dog_H.jpg',
                'height': 100, 'width': 100})
        observed = resp.text
        print(observed)

        assert observed == expected
