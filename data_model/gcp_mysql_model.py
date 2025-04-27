import sqlalchemy

from os import environ
from .base_model import BaseDBSession


class GcpMySQLDBSession(BaseDBSession):
    """
    Interfaces with GCP MySQL cloud db according to the env vars below
    """
    def __init__(self):
        db_env = environ.get("DB_ENV")  # "prod" or "test"
        db_host = environ.get("INSTANCE_HOST")  # an IP address
        db_user = environ.get("DB_USER")  # e.g. 'my-db-user'
        db_pass = environ.get("DB_PASS")  # e.g. 'my-db-password'
        db_name = environ.get("DB_NAME")  # e.g. 'my-database'
        db_port = environ.get("DB_PORT")  # e.g. 3306
        if db_port is None:
            db_port = 3306

        # https://cloud.google.com/sql/docs/mysql/samples/cloud-sql-mysql-sqlalchemy-connect-tcp-sslcerts
        # this cert will expire in 2035

        if db_env == 'prod':  # internal gcp access only, no certs given
            engine = sqlalchemy.create_engine(
                sqlalchemy.engine.url.URL.create(
                    drivername="mysql+pymysql",
                    username=db_user,
                    password=db_pass,
                    host=db_host,
                    port=db_port,
                    database=db_name))
        else:
            ssl_args = {
                'ssl_ca': 'static/test-server-ca.pem',
                # client cert & key would go here under ssl_cert & ssl_key
            }
            engine = sqlalchemy.create_engine(
                sqlalchemy.engine.url.URL.create(
                    drivername="mysql+pymysql",
                    username=db_user,
                    password=db_pass,
                    host=db_host,
                    port=db_port,
                    database=db_name),
                connect_args=ssl_args)

        super().__init__(engine)  # opens self.session for queries
