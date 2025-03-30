import sqlite3
import time
import uuid


DB_NAME = 'test.db'
TABLE_NAME = 'art'
TABLE_SCHEMA = f'{TABLE_NAME}(uid, content, timestamp)'


class Sqlite3_DB():
    def __init__(self):
        self.con = sqlite3.connect(DB_NAME)
        self.cur = self.con.cursor()


    def check_schema(self):
        # ensure there's only one table, art
        # with fields content, timestamp; create it if the db is empty
        tables = self.cur.execute("""
            SELECT name FROM sqlite_schema
            WHERE type='table'
            ORDER BY name;
            """)
        table = tables.fetchone()
        none = tables.fetchone()

        if table is None:
                self.cur.execute(f"CREATE TABLE {TABLE_SCHEMA}")
        elif table[0] != TABLE_NAME or none is not None:
            raise sqlite3.DatabaseError(f'database has fallen out of intended schema; tables: {tables}')
        print('ready to begin database operations')


    def insert_art(self, art: str):
        timestamp = time.time()
        self.cur.execute(f"INSERT INTO {TABLE_SCHEMA} VALUES(?, ?, ?)", (str(uuid.uuid4()), art, timestamp))
        self.con.commit()


    def dump_table(self):
        print('all records:')
        for record in self.cur.execute(f"SELECT * FROM {TABLE_NAME}"):
            print(record)


    def close(self):
        self.con.close()


if __name__ == '__main__':
    db = Sqlite3_DB()
    db.check_schema()
    db.insert_art('thisisatest')
    db.dump_table()
    db.close()
