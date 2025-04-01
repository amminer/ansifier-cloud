import os
import sqlalchemy
import time
import uuid

from .base_model import Base_DB


DB_NAME = 'test.db'
TABLE_NAME = 'art'
TABLE_SCHEMA = f'{TABLE_NAME}(uid, content, format, timestamp)'


class Gcp_Cloudsql_DB(Base_DB):
    def __init__(self):
        self.pool = connect_to_gcp_cloudsql()

    def check_schema(self):
        """
        ensure there's only one table, art
        with fields content, timestamp; create it if the db is empty

        the schema table's modern name is sqlite_schema, legacy name is sqlite_master
        GCP has an old enough version of sqlite3 (pre 3.30) that the legacy name is needed
        """
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
            raise sqlite3.DatabaseError(
                f'database has fallen out of intended schema; tables: {tables}')
        print('ready to begin database operations')

    def insert_art(self, art: str, format: str) -> str:
        timestamp = time.time()
        uid = str(uuid.uuid4())
        self.cur.execute(f"INSERT INTO {TABLE_SCHEMA} VALUES(?, ?, ?, ?)",
                         (uid, art, format, timestamp))
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


#if __name__ == '__main__':
    #db = Sqlite3_DB()
    #db.check_schema()
    #uid = db.insert_art('thisisatest', 'html/css')
    #print(uid, "inserted")
    #db.dump_table()
    #db.close()

def connect_to_gcp_cloudsql() -> sqlalchemy.engine.base.Engine:
    """Initializes a TCP connection pool for a Cloud SQL instance of MySQL."""
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.
    db_host = os.environ[
        "INSTANCE_HOST"
    ]  # e.g. '127.0.0.1' ('172.17.0.1' if deployed to GAE Flex)
    db_user = os.environ["DB_USER"]  # e.g. 'my-db-user'
    db_pass = os.environ["DB_PASS"]  # e.g. 'my-db-password'
    db_name = os.environ["DB_NAME"]  # e.g. 'my-database'
    db_port = os.environ["DB_PORT"]  # e.g. 3306

    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # mysql+pymysql://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
        sqlalchemy.engine.url.URL.create(
            drivername="mysql+pymysql",
            username=db_user,
            password=db_pass,
            host=db_host,
            port=db_port,
            database=db_name,
        ),
        # ...
    )
    return pool
