import time
import time
from subprocess import check_output
from sqlalchemy import text
from uuid import UUID, uuid4

from data_model.base_model import AnsiArtRecord
from tests.unit.mock_session import MockDBSession


TEST_ATTRIBUTES = {'uid': None,
                   'art': 'testartstring',
                   'format': 'ansi-escaped',
                   'timestamp': time.time(),
                   'user': None}


class TestAnsiArtRecord():
    db = MockDBSession()


    def insert_art_raw_sql(self):
        TEST_ATTRIBUTES['uid'] = str(uuid4())
        insertion_query = text(
            f'INSERT INTO art ({", ".join(k for k in TEST_ATTRIBUTES.keys() if k != "user")}) '
            f'''VALUES ({", ".join('"' + str(v) + '"' for k, v in TEST_ATTRIBUTES.items() if k != "user")});''')
        print(insertion_query)

        with self.db.engine.connect() as con:
            con.execute(insertion_query)
            con.commit()


    def test_insert_art(self):
        TEST_ATTRIBUTES['uid'] = self.db.insert_art(art=TEST_ATTRIBUTES['art'],
                                 format=TEST_ATTRIBUTES['format'],
                                 user=TEST_ATTRIBUTES['user'])
        UUID(TEST_ATTRIBUTES['uid'])  # raises exception if TEST_UID is not valid

        # independent queries decouple SQL statement from column order, but are inefficient...
        for k, v in TEST_ATTRIBUTES.items():
            if k != 'timestamp':
                expected = v

                query = text(f'SELECT {k} FROM art WHERE uid = "{TEST_ATTRIBUTES["uid"]}";')

                with self.db.engine.connect() as con:
                    observed = con.execute(query).first()[0] 
                    con.commit()

                assert observed == expected


    def test_retrieve_art(self):
        self.insert_art_raw_sql()
        print(self.db.most_recent_3())

        retrieved_art = self.db.retrieve_art(TEST_ATTRIBUTES['uid'])
        assert retrieved_art == TEST_ATTRIBUTES['art']


    def test_delete_art(self):
        self.insert_art_raw_sql()
        print(self.db.most_recent_3())

        self.db.delete_art(TEST_ATTRIBUTES['uid'])

        retrieved_art = self.db.session.execute(text(
            f'SELECT * FROM art WHERE uid = "{TEST_ATTRIBUTES["uid"]}";'
        )).first()
        assert retrieved_art is None

    # TODO test_most_recent_3?
    # TODO test negative case behaviors (uuid not found, etc)
