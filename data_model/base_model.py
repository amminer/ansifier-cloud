"""
This module defines the database that backs the application in an abstract, database-agnostic way

Concrete backends/databases should be set up independently, e.x. you might stand up a MySQL server
with a public IP, a database, a username, and a password, then define a subclass of Base_DB here
to interface with it.

To interface with such a backend, inherit from Base_DB. In the concrete DB class's __init__,
create a sqlalchemy Engine with sqlalchemy.create_engine and pass the engine to super().__init__,
which initializes a session for the lifetime of the object at self.session.
"""

import time
import uuid
from sqlalchemy import Column, Integer, String, Text, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import mysql
from abc import ABC


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


# medium.com/@ramanbazhanau/mastering-sqlalchemy-a-comprehensive-guide-for-python-developers-ddb3d9f2e829
Base = declarative_base()
class AnsiArtRecord(Base):
    __tablename__ = 'art'
    
    uid = Column(String(37), primary_key=True)
    art = Column(LongTextUniversal(), nullable=False)
    format = Column(String(64), nullable=False)
    timestamp = Column(Integer(), nullable=False)

    def __repr__(self):
        return f'AnsiArtRecord(uid={self.uid}, format={self.format}, timestamp={self.timestamp})'


class Base_DB(ABC):
    def __init__(self, engine: Engine):
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()


    def insert_art(self, art: str, format: str) -> str:
        """
        add a row to the database, one piece of ansi art
        """
        timestamp = time.time()
        uid = Base_DB.get_uuid()
        self.session.add(AnsiArtRecord(
            uid=uid,
            timestamp=timestamp,
            art=art,
            format=format))
        self.session.commit()
        return uid


    def retrieve_art(self, uid: str) -> str:
        """
        read the art out of the given uid
        returns the empty string on failed queries
        """
        query = self.session.query(AnsiArtRecord).filter_by(uid=uid)
        ret = query.first()
        if ret is None:
            raise ValueError(f'uid {uid} not found')
        print(f'retrieved {ret} from database')
        return ret.art


    def most_recent_3(self) -> str:
        """
        read the most recent 3 gallery submissions and return them as a list
        """
        ret = self.session.query(AnsiArtRecord).limit(3).all()
        return ['<br/>' + record.uid + ':<br/>' + record.art for record in ret]


    #TODO a few more db ops


    @staticmethod
    def get_uuid() -> str:
        return str(uuid.uuid4())
