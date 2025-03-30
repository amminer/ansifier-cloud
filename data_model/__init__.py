"""
Determines what database is imported by the main application for backend interactions
the database class MUST be imported here as "Database"
and MUST expose functions:
    insert_art(art)
    ...
"""
from .sqlite_model import Sqlite3_DB as Database
