import sqlalchemy
from os import environ

from .base_model import Base_DB


class Gcp_Cloudsql_DB(Base_DB):
    """
    Interfaces with GCP MySQL cloud db according to the env vars below
    """
    def __init__(self):
        db_host = environ.get("INSTANCE_HOST")  # an IP address
        db_user = environ.get("DB_USER")  # e.g. 'my-db-user'
        db_pass = environ.get("DB_PASS")  # e.g. 'my-db-password'
        db_name = environ.get("DB_NAME")  # e.g. 'my-database'
        db_port = environ.get("DB_PORT")  # e.g. 3306
        if db_port is None:
            db_port = 3306

        engine = sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL.create(
                drivername="mysql+pymysql",
                username=db_user,
                password=db_pass,
                host=db_host,
                port=db_port,
                database=db_name))
        super().__init__(engine)  # opens self.session for queries
