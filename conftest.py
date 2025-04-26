import pytest
import sqlalchemy
from data_model.base_model import BaseDBSession

class MockDBSession(BaseDBSession):
        def __init__(self):
            engine = sqlalchemy.create_engine(f'sqlite:///:memory:')
            self.engine = engine
            super().__init__(engine)

@pytest.fixture
def mock_db():
    return MockDBSession()
