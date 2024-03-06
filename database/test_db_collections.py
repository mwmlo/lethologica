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


def test_db_can_list_collections():
    with requests_mock.Mocker() as m:
        # Set behaviour of GET request to given url with expected headers
        m.get(COLLECTIONS_URL, request_headers=GET_HEADERS, status_code=HTTP_OK)
        # Conduct the test
        response = connector._list_collections()
        assert response.status_code == HTTP_OK, f"Actual response: {response.json()}"


def test_db_can_create_collection():
    vector_size = 2
    with requests_mock.Mocker() as m:
        # Set behaviour of POST request to given url with expected json and headers
        m.post(
            COLLECTIONS_URL,
            json={
                "id": TEST_COLLECTION_ID,
                "vectorSize": vector_size,
                "distanceMetric": "euclidean",
            },
            request_headers=PUT_HEADERS,
            status_code=HTTP_OK,
        )
        # Conduct the test
        response = connector._create_collection(TEST_COLLECTION_ID, vector_size)
        assert response.status_code == HTTP_OK, f"Actual response: {response.json()}"


def test_db_can_delete_collection():
    with requests_mock.Mocker() as m:
        # Set behaviour of DELETE request to given url with expected headers
        m.delete(
            f"{COLLECTIONS_URL}/{TEST_COLLECTION_ID}",
            request_headers=GET_HEADERS,
            status_code=HTTP_OK,
        )
        # Conduct the test
        response = connector._delete_collection(TEST_COLLECTION_ID)
        assert response.status_code == HTTP_OK, f"Actual response: {response.json()}"
