import pytest
from populate_db import populate

from database.db_connector import DBConnector

connector = DBConnector(test=True)

# Constants used by the tests
TEST_COLLECTION_ID = "testid"
HTTP_OK = 200


@pytest.fixture(autouse=True)
def cleanup():
    # Run test first
    yield
    # Delete any test collections created
    connector._delete_collection(TEST_COLLECTION_ID)


def test_populate_adds_data():
    populate(2, TEST_COLLECTION_ID, test=True)
    response = connector._list_collections()
    assert response.status_code == HTTP_OK, f"Actual response: {response.json()}"
    assert response.json()["collections"][0]["id"] == TEST_COLLECTION_ID
