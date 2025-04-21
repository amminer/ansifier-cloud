import sqlalchemy

from .base_model import Base_DB


DB_NAME = 'test.db'


class Sqlite3_DB(Base_DB):
    def __init__(self):
        engine = sqlalchemy.create_engine(f'sqlite:///{DB_NAME}')
        super().__init__(engine)
