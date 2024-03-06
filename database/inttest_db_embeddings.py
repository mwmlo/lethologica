import numpy as np
import pytest
from db_connector import DBConnector

connector = DBConnector(test=True)

# Constants used by the tests
TEST_COLLECTION_ID = "testid"
HTTP_OK = 200
EMBEDDINGS = np.array([[1, 2], [3, 4]])
WORDS = ["word one", "word 2"]
DEFINITIONS = ["definition one", "definition 2"]


@pytest.fixture(autouse=True)
def cleanup():
    # Set up collection
    create_response = connector._create_collection(TEST_COLLECTION_ID, 2)
    assert create_response.status_code == HTTP_OK
    # Run test
    yield
    # Delete any test collections created
    delete_response = connector._delete_collection(TEST_COLLECTION_ID)
    assert delete_response.status_code == HTTP_OK


def test_can_insert_embedding():
    response = connector.insert_embeddings(
        TEST_COLLECTION_ID, EMBEDDINGS, WORDS, DEFINITIONS
    )
    assert response.status_code == HTTP_OK, f"Actual response: {response.json()}"
    assert (
        response.json()["message"] == "success"
    ), f"Actual response: {response.json()}"


def test_can_delete_embedding():
    # Insert test embeddings
    insert = connector.insert_embeddings(
        TEST_COLLECTION_ID, EMBEDDINGS, WORDS, DEFINITIONS
    )
    assert insert.status_code == HTTP_OK
    # Get a list of embedding IDs for the closest match (which should be exact)
    matches = connector.get_matches(TEST_COLLECTION_ID, EMBEDDINGS[0])
    assert matches.status_code == HTTP_OK
    embedding_ids = [matches.json()["points"][0]["id"]]
    # Delete embedding
    response = connector.delete_embeddings(TEST_COLLECTION_ID, embedding_ids)
    assert response.status_code == HTTP_OK, f"Actual response: {response.json()}"
    assert (
        response.json()["message"] == "success"
    ), f"Actual response: {response.json()}"


def test_can_search_embeddings():
    # Insert test embeddings
    insert = connector.insert_embeddings(
        TEST_COLLECTION_ID, EMBEDDINGS, WORDS, DEFINITIONS
    )
    assert insert.status_code == HTTP_OK
    # Get a list of embedding IDs for the closest match (which should be exact)
    response = connector.get_matches(TEST_COLLECTION_ID, EMBEDDINGS[0])
    assert response.status_code == HTTP_OK, f"Actual response: {response.json()}"
    assert response.json()["points"][0]["metadata"]["word"] == WORDS[0]
    assert response.json()["points"][0]["metadata"]["def"] == DEFINITIONS[0]
