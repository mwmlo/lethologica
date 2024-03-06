import json
import os
import sys

import pytest
import requests_mock
from flaskr import create_app
from flaskr.views import HTTP_OK, PROD_COLLECTION_ID

from database.db_connector import DBConnector

# Required for pytest to be able to import the correct files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))


# Constants used by the tests. API key is sourced from the DB connector.
connector = DBConnector()
HTTP_ERROR = 503
RATE_LIMIT_ERROR = 429
SEARCH_URL = (
    f"https://semadb.p.rapidapi.com/collections/{PROD_COLLECTION_ID}/points/search"
)
PUT_HEADERS = {
    "content-type": "application/json",
    "X-RapidAPI-Key": connector.api_key,
    "X-RapidAPI-Host": "semadb.p.rapidapi.com",
}
WORDS = ["word one", "word 2"]
DEFINITIONS = ["definition one", "definition 2"]
POS = ["noun", "verb"]
EXAMPLES = ["ex1", "ex2"]
SEARCH_PAYLOAD = {
    "points": [
        {
            "distance": 0,
            "metadata": {
                "word": WORDS[0],
                "def": DEFINITIONS[0],
                "pos": POS[0],
                "ex": EXAMPLES[0],
            },
        },
        {
            "distance": 1,
            "metadata": {
                "word": WORDS[1],
                "def": DEFINITIONS[1],
                "pos": POS[1],
                "ex": EXAMPLES[1],
            },
        },
    ]
}
TEST_EMBEDDING = {
    "dims": [1, 768],
    "type": "float32",
    "data": {str(n): 1.0 for n in range(0, 768)},
    "size": 768,
}
DATA_PAYLOAD = {
    "def": "some definition",
    "embedding_input": json.dumps(TEST_EMBEDDING),
    "spellchecked_input": "",
}

DATA_PAYLOAD_MISSPELLED = {
    "def": "some definitin",
    "embedding_input": json.dumps(TEST_EMBEDDING),
    "spellchecked_input": "some definition",
}


@pytest.fixture()
def app():
    app = create_app(enable_limits=False, csrf_enabled=False)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_content(client):
    response = client.get("/")
    assert b"<h1>Lethologica</h1>" in response.data


def test_form_submit(client):
    with requests_mock.Mocker() as mock_db:
        mock_db.post(
            SEARCH_URL,
            json=SEARCH_PAYLOAD,
            request_headers=PUT_HEADERS,
            status_code=HTTP_OK,
        )
        response = client.post(
            "/",
            data=DATA_PAYLOAD,
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        assert b"<h1>Lethologica</h1>" in response.data


def test_form_submit_empty(client):
    response = client.post(
        "/",
        data={"def": ""},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert b"Please enter a valid definition!" in response.data


def test_displays_definition(client):
    with requests_mock.Mocker() as mock_db:
        mock_db.post(
            SEARCH_URL,
            json=SEARCH_PAYLOAD,
            request_headers=PUT_HEADERS,
            status_code=HTTP_OK,
        )
        response = client.post(
            "/",
            data=DATA_PAYLOAD,
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        assert b'Results for "some definition"' in response.data


def test_displays_matches(client):
    # Set up a mocked database
    with requests_mock.Mocker() as mock_db:
        mock_db.post(
            SEARCH_URL,
            json=SEARCH_PAYLOAD,
            request_headers=PUT_HEADERS,
            status_code=HTTP_OK,
        )
        # Check returned display
        response = client.post(
            "/",
            data=DATA_PAYLOAD,
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        assert WORDS[0].encode("UTF-8") in response.data
        assert WORDS[1].encode("UTF-8") in response.data


def test_displays_matches_without_duplicates(client):
    # Set up a mocked database
    with requests_mock.Mocker() as mock_db:
        payload_with_duplicate = SEARCH_PAYLOAD
        payload_with_duplicate["points"].append(payload_with_duplicate["points"][1])
        mock_db.post(
            SEARCH_URL,
            json=payload_with_duplicate,
            request_headers=PUT_HEADERS,
            status_code=HTTP_OK,
        )
        # Check returned display
        response = client.post(
            "/",
            data=DATA_PAYLOAD,
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        assert (
            response.data.count(WORDS[1].encode("UTF-8")) == 2
        )  # once in body, once in script to show more


def test_displays_error_when_db_fails(client):
    # Set up a mocked database
    with requests_mock.Mocker() as mock_db:
        mock_db.post(
            SEARCH_URL,
            json=SEARCH_PAYLOAD,
            request_headers=PUT_HEADERS,
            status_code=HTTP_ERROR,
        )
        # Check returned display
        response = client.post(
            "/",
            data=DATA_PAYLOAD,
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        assert b"Sorry, no results available" in response.data


def test_displays_warning_when_typo(client):
    # Set up a mocked database
    with requests_mock.Mocker() as mock_db:
        mock_db.post(
            SEARCH_URL,
            json=SEARCH_PAYLOAD,
            request_headers=PUT_HEADERS,
            status_code=HTTP_OK,
        )
        # Check returned display
        response = client.post(
            "/",
            data=DATA_PAYLOAD_MISSPELLED,
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        assert b"Potential spelling mistake" in response.data


def test_displays_suggestion_when_typo(client):
    # Set up a mocked database
    with requests_mock.Mocker() as mock_db:
        mock_db.post(
            SEARCH_URL,
            json=SEARCH_PAYLOAD,
            request_headers=PUT_HEADERS,
            status_code=HTTP_OK,
        )
        # Check returned display
        response = client.post(
            "/",
            data=DATA_PAYLOAD_MISSPELLED,
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        assert b'"some definition"' in response.data


def test_get_rate_limit():
    # Create rate limited application
    app = create_app(enable_limits=True, csrf_enabled=False)
    with app.test_client() as client:
        # Limit: 5 requests per second
        for _ in range(6):
            response = client.get("/")
        assert response.status_code == RATE_LIMIT_ERROR


def test_post_rate_limit(client):
    with requests_mock.Mocker() as mock_db:
        mock_db.post(
            SEARCH_URL,
            json=SEARCH_PAYLOAD,
            request_headers=PUT_HEADERS,
            status_code=HTTP_ERROR,
        )
        # Create rate limited application
        app = create_app(enable_limits=True, csrf_enabled=False)
        with app.test_client() as client:
            # Limit: 5 requests per second
            for _ in range(6):
                response = client.post(
                    "/",
                    data=DATA_PAYLOAD,
                    headers={"content-type": "application/x-www-form-urlencoded"},
                )
            assert response.status_code == RATE_LIMIT_ERROR
