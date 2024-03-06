import pytest
from db_connector import DBConnector

connector = DBConnector(test=True)

# Constants used by the tests
TEST_COLLECTION_ID = "testid"
HTTP_OK = 200
HTTP_CONFLICT = 409


@pytest.fixture(autouse=True)
def cleanup():
    # Run test first
    yield
    # Delete any test collections created
    connector._delete_collection(TEST_COLLECTION_ID)


def test_db_can_list_collections():
    response = connector._list_collections()
    assert response.status_code == HTTP_OK, f"Actual response: {response.json()}"


def test_db_can_create_collection():
    response = connector._create_collection(TEST_COLLECTION_ID, 2)
    assert response.status_code == HTTP_OK, f"Actual response: {response.json()}"


def test_db_can_delete_collection():
    connector._create_collection(TEST_COLLECTION_ID, 2)
    response = connector._delete_collection(TEST_COLLECTION_ID)
    assert response.status_code == HTTP_OK, f"Actual response: {response.json()}"


def test_created_collection_persists():
    connector._create_collection(TEST_COLLECTION_ID, 2)
    response = connector._list_collections()
    assert response.status_code == HTTP_OK, f"Actual status: {response.status_code}"
    assert len(response.json()["collections"]) == 1


def test_cannot_create_duplicate_collections():
    first_response = connector._create_collection(TEST_COLLECTION_ID, 2)
    assert (
        first_response.status_code == HTTP_OK
    ), f"Actual response: {first_response.json()}"
    second_response = connector._create_collection(TEST_COLLECTION_ID, 2)
    assert (
        second_response.status_code == HTTP_CONFLICT
    ), f"Actual response: {second_response.json()}"
