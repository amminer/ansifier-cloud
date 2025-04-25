"""
This module defines the database that backs the application in an abstract, database-agnostic way

Concrete backends/databases should be set up independently, e.x. you might stand up a MySQL server
with a public IP, a database, a username, and a password, then define a subclass of BaseDBSession here
to interface with it.

To interface with such a backend, inherit from BaseDBSession. In the concrete DB class's __init__,
create a sqlalchemy Engine using sqlalchemy.create_engine and pass the engine to super().__init__,
which initializes a Session for the lifetime of the object at self.session.
"""

import time
import uuid

from abc import ABC
from sqlalchemy import Column, Integer, String, Text, TypeDecorator, desc
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects import mysql
from werkzeug.security import generate_password_hash, check_password_hash


MAX_USERNAME_LEN = 30


# MySQL Compatibility
# 
# docs.sqlalchemy.org/en/20/core/custom_types.html#sqlalchemy.types.TypeDecorator.load_dialect_impl
class LongTextUniversal(TypeDecorator):
    """
    ansi arts are really long strings - with sufficient dimensions they're big enough
    that they really ought to be stored in files and pointed to from the database.
    However, I don't want to deal with that right now,
    so I'm limiting the dimensions to somewhere around 300x300, which should keep output <= 1 MB.
    This is small enough that it can reasonably be stored directly in the database;
    Many dialects have a single text type with variadic sizing and very high limits
    (e.x. 1 GB for PostgreSQL).
    However, MySQL defines several text column types with different max lengths...
    sqlalchemy's Text type maps to a MySQL type with a max size of just 64 KB.
    This class exists to patch this unfortunate quirk at the intersection of MySQL and sqlalchemy,
    and may be used in the future to accomodate other dialectical oddities as they're learned.
    """
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'mysql':
            return dialect.type_descriptor(mysql.LONGTEXT())
        return dialect.type_descriptor(Text())


# Table definitions/Models
#
# https://docs.sqlalchemy.org/en/20/orm/mapping_api.html#sqlalchemy.orm.declarative_base
BaseRecord = declarative_base()

class AnsiArtRecord(BaseRecord):
    __tablename__ = 'art'
    uid = Column(String(37), primary_key=True)
    art = Column(LongTextUniversal(), nullable=False)
    format = Column(String(64), nullable=False)
    timestamp = Column(Integer(), nullable=False)
    user = Column(String(MAX_USERNAME_LEN), nullable=True)

    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'AnsiArtRecord(uid={self.uid}, format={self.format}, timestamp={self.timestamp})'

    def insert_art(self, art: str, format: str, user=None) -> str:
        """
        add a row to the database, one piece of ansi art
        """
        timestamp = time.time()
        uid = BaseDBSession.get_uuid()
        self.session.add(AnsiArtRecord(
            uid=uid,
            timestamp=timestamp,
            art=art,
            format=format,
            user=user))
        self.session.commit()
        return uid

    def retrieve_art(self, uid: str) -> str:
        """
        read the art out of the given uid
        returns the empty string on failed queries
        """
        # TODO user must be None
        # TODO add a routine for retrieving user's private rows
        query = self.session.query(AnsiArtRecord).filter_by(uid=uid)
        ret = query.first()
        if ret is None:
            raise ValueError(f'uid {uid} not found')
        print(f'retrieved {ret} from database')
        return ret.art  # return other columns too?

    def delete_art(self, uid: str) -> None:
        query = self.session.query(AnsiArtRecord).filter_by(uid=uid)
        query.delete()
        self.session.commit()

    def most_recent_3(self) -> str:
        """
        read the most recent 3 gallery submissions and return them as a list
        """
        query = self.session.query(AnsiArtRecord).order_by(desc(AnsiArtRecord.timestamp)).limit(3)
        ret = query.all()
        return ['<br/>' + record.uid + ':<br/>' + record.art for record in ret]


class UserRecord(BaseRecord):
    __tablename__ = 'users'
    username = Column(String(MAX_USERNAME_LEN), primary_key=True)
    password_hash = Column(String(150), nullable=False)
    account_created_time = Column(Integer(), nullable=False)
    def __init__(self, session=None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'UserRecord(username={self.username})'

    def create_user(self, username, password):
        pass  # TODO

    def delete_user(self, password):
        pass  # TODO

    def login(self, username, password):
        pass  # TODO

    def logout(self):
        pass  # TODO


# Database Session handler
#
#
class BaseDBSession(ABC):
    """
    Exposes database query routines
    TODO separate concerns of session management vs query logic without breaking interface
    """
    def __init__(self, engine: Engine):
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.username = None

        BaseRecord.metadata.create_all(engine)
        self._records = [
            AnsiArtRecord(self.session),
            UserRecord(self.session)
        ]
        self._register_record_methods()


    def _register_record_methods(self):
        """
        this makes sense to do at runtime right now, because it's easier to maintain self._records
        than it is to manually maintain a set of wrapper functions, but it may hurt observability
        or confuse development tooling, LSP, typecheckers
        """
        for Record in self._records:
            for name in dir(Record):
                if name.startswith('_'):
                    continue
                attr = getattr(Record, name)
                if callable(attr) and not hasattr(self, name):
                    setattr(self, name, attr)  # TODO does this hurt debugability? functools.wrap?


    @staticmethod
    def get_uuid() -> str:
        return str(uuid.uuid4())
