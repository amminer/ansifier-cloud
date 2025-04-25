import sqlalchemy

from .base_model import BaseDBSession


DB_NAME = 'test.db'


class Sqlite3DBSession(BaseDBSession):
    def __init__(self):
        engine = sqlalchemy.create_engine(f'sqlite:///{DB_NAME}')
        super().__init__(engine)
