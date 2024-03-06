import json
import os
import sys

# Required for pytest to be able to import the correct files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import flask
import pytest
import requests_mock
from flaskr import create_app
from flaskr.views import FORBIDDEN_ERR

TEST_EMBEDDING = {
    "dims": [1, 768],
    "type": "float32",
    "data": {str(n): 1.0 for n in range(0, 768)},
    "size": 768,
}


@pytest.fixture()
def app():
    app = create_app(csrf_enabled=True)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_invalid_csrf_token(client):
    with requests_mock.Mocker() as mock_db:
        response = client.post(
            "/",
            data={
                "def": "test",
                "embedding_input": json.dumps(TEST_EMBEDDING),
                "spellchecked_input": "",
            },
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        assert b"<title>CSRF Error</title>" in response.data
        assert response.status_code == FORBIDDEN_ERR


def test_valid_csrf_token(app):
    with app.app_context(), app.test_client(use_cookies=True) as c:
        c.get("/")  # Generate CSRF token when reaching initial page
        response = c.post(
            "/",
            data={
                "def": "test",
                "embedding_input": json.dumps(TEST_EMBEDDING),
                "csrf_token": flask.g.csrf_token,
                "spellchecked_input": "",
            },
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        assert b"<h1>Lethologica</h1>" in response.data
