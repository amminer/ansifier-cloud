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

        if db_env == 'prod':
            ssl_ca ='static/prod-server-ca.pem' 
        else:
            ssl_ca = 'static/test-server-ca.pem' 

        # https://cloud.google.com/sql/docs/mysql/samples/cloud-sql-mysql-sqlalchemy-connect-tcp-sslcerts
        # this cert will expire in 2035

        ssl_args = {
            'ssl_ca': ssl_ca,
            # client cert & key would go here under ssl_cert & ssl_key
        }
        print('forming login URL')
        url = sqlalchemy.engine.url.URL.create(
            drivername="mysql+pymysql",
            username=db_user,
            password=db_pass,
            host=db_host,
            port=db_port,
            database=db_name)
        print(f'logging into {db_host} port {db_port} db {db_name} with username {db_user} and password {db_pass}')
        engine = sqlalchemy.create_engine(url, connect_args=ssl_args)
        print(f'engine {engine}')

        super().__init__(engine)  # opens self.session for queries
