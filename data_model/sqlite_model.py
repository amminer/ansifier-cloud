import sqlite3
import time

from .base_model import Base_DB, TABLE_NAME, TABLE_SCHEMA


DB_NAME = 'test.db'


class Sqlite3_DB(Base_DB):
    def __init__(self):
        self.con = sqlite3.connect(DB_NAME)
        self.cur = self.con.cursor()


    def check_schema(self):
        # ensure there's only one table, art
        # with fields content, timestamp; create it if the db is empty
        #
        # the schema table's modern name is sqlite_schema, legacy name is sqlite_master
        # GCP has an old enough version of sqlite3 (pre 3.30) that the legacy name is needed
        tables = self.cur.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
            ORDER BY name;
            """)
        table = tables.fetchone()
        none = tables.fetchone()

        if table is None:
                self.cur.execute(f"CREATE TABLE {TABLE_SCHEMA}")
        elif table[0] != TABLE_NAME or none is not None:
            raise sqlite3.DatabaseError(f'database has fallen out of intended schema; tables: {tables}')


    def insert_art(self, art: str, format: str) -> str:
        timestamp = time.time()
        uid = Base_DB.get_uuid()
        self.cur.execute(f"INSERT INTO {TABLE_SCHEMA} VALUES(?, ?, ?, ?)", (uid, art, format, timestamp))
        self.con.commit()
        return uid


    def retrieve_art(self, uid: str):
        ret = self.cur.execute(f"SELECT content FROM {TABLE_NAME} WHERE uid='{uid}'").fetchone()
        if ret is None:
            return ''
        return ret[0]


    def most_recent_3(self):
        ret = self.cur.execute(f"SELECT content FROM {TABLE_NAME} ORDER BY timestamp DESC LIMIT 3;")
        return [a[0] for a in ret]


    def dump_table(self):
        print('all records:')
        for record in self.cur.execute(f"SELECT * FROM {TABLE_NAME}"):
            print(record)


    def close(self):
        self.con.close()
