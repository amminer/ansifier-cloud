"""
Exposes database classes to the main application
via the get_database factory method:
    from data_model import get_database
    DB = get_database(db_name)
Database classes must implement the Base_DB abstract class.
"""
from .base_model import Base_DB
from .sqlite_model import Sqlite3_DB


db_options = {
    'sqlite3': Sqlite3_DB,
}


def get_database(db_name: str) -> Base_DB:
    """
    looks db_name up in db_options and ensures that a valid database implementation is found
    before returning an instance of the concrete database class
    otherwise, raises an exception regarding the absence or invalidity of a matching implementation
    """
    database_class = db_options.get(db_name, None)
    if database_class is None:
        raise ValueError(f'invalid database type requested by application "{db_name}"')
    if not issubclass(database_class, Base_DB):
        raise Exception(f'database type "{db_name}" links to "{database_class}", '
                        'which is not a valid database interface implementation')
    return database_class()
