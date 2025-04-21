# TODO https://docs.sqlalchemy.org/en/13/core/tutorial.html
import os
import sqlalchemy
import time
from sqlite3 import DatabaseError

from .base_model import Base_DB, TABLE_NAME


TABLE_SCHEMA_TYPED = f'{TABLE_NAME}(uid TEXT, content TEXT, format TEXT, timestamp INT)'  # TODO dry this out
TABLE_SCHEMA = f'{TABLE_NAME}(uid, content, format, timestamp)'  # TODO dry this out


class Gcp_Cloudsql_DB(Base_DB):
    """
    Interfaces with GCP MySQL cloud db according to the following env vars:
    INSTANCE_HOST
    DB_USER
    DB_PASS
    DB_NAME
    DB_PORT
    """
    def __init__(self):
        self.pool = connect_to_gcp_cloudsql()


    def check_schema(self):
        with self.pool.connect() as conn:
            tables = conn.execute(sqlalchemy.text("SHOW TABLES;"))
            table = tables.fetchone()
            none = tables.fetchone()

            if table is None:
                    conn.execute(sqlalchemy.text(f"CREATE TABLE {TABLE_SCHEMA_TYPED};"))
            elif table[0] != TABLE_NAME or none is not None:
                raise DatabaseError(f'database has fallen out of intended schema; tables: '
                                    + str(tables.fetchall()))
        print('ready to begin database operations')


    def insert_art(self, art: str, format: str) -> str:
        timestamp = time.time()
        uid = Base_DB.get_uuid()
        with self.pool.connect() as conn:
            conn.execute(sqlalchemy.text(  # TODO SQL syntax... need to learn SQL Expression Lang (see line 1)
                f'INSERT INTO {TABLE_SCHEMA} VALUES({uid}, {art}, {format}, {timestamp})'))
            conn.commit()
        return uid


    def retrieve_art(self, uid: str) -> str:
        return "TODO"


    def most_recent_3(self) -> str:
        return "TODO"


    def dump_table(self):
        print('all records:')
        print('TODO')


    def close(self):
        print('TODO')


def connect_to_gcp_cloudsql() -> sqlalchemy.engine.base.Engine:
    """Initializes a TCP connection pool for a Cloud SQL instance of MySQL."""
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.
    # TODO rename these
    db_host = os.environ.get("INSTANCE_HOST")  # an IP address
    db_user = os.environ.get("DB_USER")  # e.g. 'my-db-user'
    db_pass = os.environ.get("DB_PASS")  # e.g. 'my-db-password'
    db_name = os.environ.get("DB_NAME")  # e.g. 'my-database'
    db_port = os.environ.get("DB_PORT")  # e.g. 3306
    if db_port is None:
        db_port = 3306

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
