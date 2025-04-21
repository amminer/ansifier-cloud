import uuid
from abc import ABC, abstractmethod


DB_NAME = 'test.db'
TABLE_NAME = 'art'


class Base_DB(ABC):

    @abstractmethod
    def check_schema(self) -> None:
        """
        ensure there's only one table, art
        with fields content, timestamp; create it if the db is empty
        raises an exception if the db is out of order TODO DatabaseException wrapper
        """
        pass


    @abstractmethod
    def insert_art(self, art: str, format: str) -> str:
        """
        add a row to the database, one piece of ansi art
        """
        pass


    @abstractmethod
    def retrieve_art(self, uid: str) -> str:
        """
        read the art out of the given uid
        returns the empty string on failed queries
        """
        pass


    def most_recent_3(self) -> str:
        """
        read the most recent 3 gallery submissions and return them as a list
        """
        pass


    #TODO a few more db ops


    @abstractmethod
    def dump_table(self) -> None:
        """
        print the contents of the db to the console
        """
        pass


    @abstractmethod
    def close(self) -> None:
        """
        terminate database connections
        """
        pass

    @staticmethod
    def get_uuid() -> str:
        return str(uuid.uuid4())
