import time

from .base_model import Base_DB, TABLE_NAME, TABLE_SCHEMA


class Gcp_Cloudsql_DB(Base_DB):

    def check_schema(self) -> None:
        pass  #TODO


    def insert_art(self, art: str) -> str:
        pass  #TODO
        return 'THISISATEST'


    def retrieve_art(self, uid: str) -> str:
        pass  #TODO
        return 'THISISATEST'


    def most_recent_3(self) -> str:
        pass  #TODO
        return 'THISISATEST'


    def dump_table(self) -> None:
        pass  #TODO


    def close(self) -> None:
        pass  #TODO
