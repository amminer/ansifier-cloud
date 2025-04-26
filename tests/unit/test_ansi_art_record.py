import time
from sqlalchemy import text
from uuid import UUID, uuid4


TEST_ART = {'uid': None,
    'art': 'testartstring',
    'format': 'ansi-escaped',
    'timestamp': time.time(),
    'user': None}


class TestAnsiArtRecord():

    def insert_art_raw_sql(self, mock_db):
        TEST_ART['uid'] = str(uuid4())
        insertion_query = text(
            f'INSERT INTO art ({", ".join(k for k in TEST_ART.keys())}) '
            f'''VALUES ({", ".join('"' + str(v) + '"' for k, v in TEST_ART.items())});''')
        with mock_db.engine.connect() as con:
            con.execute(insertion_query)
            con.commit()

    def select_art_raw_sql(self, uid, mock_db):
        query = text(f'SELECT * FROM art WHERE uid="{uid}"')
        with mock_db.engine.connect() as con:
            result = con.execute(query)
        return result.first()

    def test_insert_art(self, mock_db):
        TEST_ART['uid'] = mock_db.insert_art(art=TEST_ART['art'],
                                 format=TEST_ART['format'],
                                 user=TEST_ART['user'])
        UUID(TEST_ART['uid'])  # raises exception if TEST_UID is not valid
        # independent queries decouple SQL statement from column order, but are inefficient...
        for k, v in TEST_ART.items():
            if k != 'timestamp':
                expected = v
                query = text(f'SELECT {k} FROM art WHERE uid = "{TEST_ART["uid"]}";')
                with mock_db.engine.connect() as con:
                    observed = con.execute(query).first()[0] 
                assert observed == expected, f'expected art attr {expected}, found {observed}'

    def test_retrieve_art(self, mock_db):
        self.insert_art_raw_sql(mock_db)
        inserted_user = self.select_art_raw_sql(TEST_ART['uid'], mock_db)
        assert inserted_user[0] == TEST_ART['uid'],\
            f'test setup: inserted user {TEST_ART["uid"]}'
        retrieved_art = mock_db.retrieve_art(TEST_ART['uid'])
        assert retrieved_art == TEST_ART['art'],\
            f'db code retrieved {TEST_ART["art"]}, expected {retrieved_art}'

    def test_delete_art(self, mock_db):
        self.insert_art_raw_sql(mock_db)
        mock_db.delete_art(TEST_ART['uid'])
        retrieved_art = self.select_art_raw_sql(TEST_ART['uid'], mock_db)
        assert retrieved_art is None,\
            f'expected None when retrieving deleted art, found {retrieved_art}'

    # TODO test_most_recent_3?
    # TODO test negative case behaviors (uuid not found, etc)
