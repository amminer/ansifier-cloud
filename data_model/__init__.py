"""
Determines what database is imported by the main application for backend interactions
the database class MUST be imported here as "Database"
and MUST expose functions:
    insert_art(art)
    ...
"""
from os import environ
from .base_model import Base_DB

from .sqlite_model import Sqlite3_DB
from .gcp_cloudsql_model import Gcp_Cloudsql_DB

databases = {
        'Sqlite3': Sqlite3_DB,
        'Gcp': Gcp_Cloudsql_DB
}


database = environ.get('ANSIFIER_DATABASE', None)
if database is None:
    raise ValueError('env var ANSIFIER_DATABASE not set')

Database = databases.get(database)
if Database is None:
    raise ValueError(f'{database} is not a valid database name, must be one of: '
                     + ', '.join(databases.keys()))

assert issubclass(Database, Base_DB)
