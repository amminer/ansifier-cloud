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
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from abc import ABC


# a little bigger than a sample 500x500 html/css output,
# currently server code restricts outputs to 333x333 so this is overhead
MAX_ART_LEN = 3100000  


# https://medium.com/@ramanbazhanau/mastering-sqlalchemy-a-comprehensive-guide-for-python-developers-ddb3d9f2e829
Base = declarative_base()
class AnsiArtRecord(Base):
    __tablename__ = 'art'
    
    uid = Column(String(37), primary_key=True)
    art = Column(String(MAX_ART_LEN), nullable=False)
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
        # TODO err handling on bad UID?
        query = self.session.query(AnsiArtRecord).filter_by(uid=uid)
        ret = query.first()
        print(f'retrieved {ret} from database')
        return ret.art


    def most_recent_3(self) -> str:
        """
        read the most recent 3 gallery submissions and return them as a list
        """
        print("TODO")
        return ["TODO", "TODO", "TODO"]


    def dump_table(self) -> None:
        """
        print the contents of the db to the console
        """
        print("TODO")


    #TODO a few more db ops


    @staticmethod
    def get_uuid() -> str:
        return str(uuid.uuid4())
