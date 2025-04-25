"""
Determines what database is imported by the main application for backend interactions
the database class MUST be imported here as "Database"
and MUST expose functions:
    insert_art(art)
    ...
"""
from os import environ
from .base_model import BaseDBSession

from .sqlite_model import Sqlite3DBSession
from .gcp_mysql_model import GcpMySQLDBSession

databases = {
        'Sqlite3': Sqlite3DBSession,
        'Gcp': GcpMySQLDBSession
}


database = environ.get('ANSIFIER_DATABASE', None)
if database is None:
    raise ValueError('env var ANSIFIER_DATABASE not set')

Database = databases.get(database)
if Database is None:
    raise ValueError(f'{database} is not a valid database name, must be one of: '
                     + ', '.join(databases.keys()))

assert issubclass(Database, BaseDBSession)
