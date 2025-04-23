import requests


class TestAnsifyfile():
    def test_ansify_file(self):
        """
        Tests whether the /ansify endpoint produces expected output for a sample file
        """

        with open('./tests/static/test_ansify_file_expected.txt', 'r') as rf:
            expected = rf.read()

        with open('./tests/test.png', 'rb') as rbf:
            resp = requests.post(
                'http://localhost:5000/ansify',
                files={'file': ('test.png', rbf)},
                data={'height': 100, 'width': 100})
        observed = resp.text
        print(observed)

        assert observed == expected
