import numpy as np
import requests_mock
from db_connector import DBConnector

connector = DBConnector(test=True)

# Constants used by the tests. API key is sourced from the DB connector.
TEST_COLLECTION_ID = "testid"
HTTP_OK = 200
COLLECTIONS_URL = "https://semadb.p.rapidapi.com/collections"
RAPIDAPI_HOST = "semadb.p.rapidapi.com"
PUT_HEADERS = {
    "content-type": "application/json",
    "X-RapidAPI-Key": connector.api_key,
    "X-RapidAPI-Host": RAPIDAPI_HOST,
}
GET_HEADERS = {"X-RapidAPI-Key": connector.api_key, "X-RapidAPI-Host": RAPIDAPI_HOST}
EMBEDDINGS = np.array([[0.5, 0.5], [0.2, 0.8]])
NORMAL_EMBEDDINGS = EMBEDDINGS / np.linalg.norm(EMBEDDINGS, axis=1, keepdims=True)
WORDS = ["word one", "word 2"]
DEFINITIONS = ["definition one", "definition 2"]
INSERT_PAYLOAD = {
    "points": [
        {
            "vector": NORMAL_EMBEDDINGS[0].tolist(),
            "metadata": {"word": WORDS[0], "def": DEFINITIONS[0], "pos": "", "ex": ""},
        },
        {
            "vector": NORMAL_EMBEDDINGS[1].tolist(),
            "metadata": {"word": WORDS[1], "def": DEFINITIONS[1], "pos": "", "ex": ""},
        },
    ]
}
SEARCH_PAYLOAD = {
    "points": [
        {
            "distance": 0,
            "metadata": {"word": WORDS[0], "def": DEFINITIONS[0], "pos": "", "ex": ""},
        },
        {
            "distance": 1,
            "metadata": {"word": WORDS[1], "def": DEFINITIONS[1], "pos": "", "ex": ""},
        },
    ]
}


def test_can_insert_embedding():
    # Checks a request contains the expected payload
    def insertion_payload_matches(request):
        return (request.json() or {}) == INSERT_PAYLOAD

    with requests_mock.Mocker() as m:
        # Set behaviour of POST request to given url with expected json and headers
        # Only match request if it contains the expected payload
        m.post(
            f"{COLLECTIONS_URL}/{TEST_COLLECTION_ID}/points",
            additional_matcher=insertion_payload_matches,
            request_headers=PUT_HEADERS,
            status_code=HTTP_OK,
        )
        # Conduct the test (insert embeddings)
        response = connector.insert_embeddings(
            TEST_COLLECTION_ID, EMBEDDINGS, WORDS, DEFINITIONS
        )
        assert response.status_code == HTTP_OK, f"Actual response: {response.json()}"


def test_can_search_embeddings():
    target_embedding = EMBEDDINGS[0]
    target_embedding_norm = NORMAL_EMBEDDINGS[0]

    # Checks a request payload contains the target embedding
    def search_payload_matches(request):
        return (request.json() or {}) == {
            "vector": target_embedding_norm.tolist(),
            "limit": 75,
        }

    with requests_mock.Mocker() as m:
        # Set behaviour of POST request to given url with expected json and headers
        # Only match request if it contains the target embedding
        m.post(
            f"{COLLECTIONS_URL}/{TEST_COLLECTION_ID}/points/search",
            additional_matcher=search_payload_matches,
            json=SEARCH_PAYLOAD,
            request_headers=PUT_HEADERS,
            status_code=HTTP_OK,
        )
        # Conduct the test (get a list of embedding IDs for the closest, in this case exact, match)
        response = connector.get_matches(TEST_COLLECTION_ID, target_embedding)
        assert response.status_code == HTTP_OK, f"Actual response: {response.json()}"
        assert response.json()["points"][0]["metadata"]["word"] == WORDS[0]
        assert response.json()["points"][0]["metadata"]["def"] == DEFINITIONS[0]


def test_can_delete_embedding():
    embedding_ids = ["this is a unique id"]

    # Checks a request payload contains the expected embedding ids
    def deletion_payload_matches(request):
        print(request.json())
        return (request.json() or {}) == {"ids": embedding_ids}

    with requests_mock.Mocker() as m:
        # Set behaviour of DELETE request to given url with expected headers
        # Only match request if it contains the expected embedding ids
        m.delete(
            f"{COLLECTIONS_URL}/{TEST_COLLECTION_ID}/points",
            additional_matcher=deletion_payload_matches,
            request_headers=PUT_HEADERS,
            status_code=HTTP_OK,
        )
        # Conduct the test (delete embedding)
        response = connector.delete_embeddings(TEST_COLLECTION_ID, embedding_ids)
        assert response.status_code == HTTP_OK, f"Actual response: {response.json()}"
