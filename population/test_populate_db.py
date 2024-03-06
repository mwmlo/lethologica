import numpy
import requests
from populate_db import populate

# Constants used by the tests
TEST_COLLECTION_ID = "testid"
TRANSFORMER_VECTOR_SIZE = 768
DISTANCE_METRIC = "cosine"

ALT_MODEL_NAME = "distiluse-base-multilingual-cased-v2"
ALT_VECTOR_SIZE = 512
ALT_DISTANCE_METRIC = "euclidean"

OK_REPONSE = requests.Response()
OK_REPONSE.status_code = 200


def mock_create_collection(_, collection_id, vector_size, distance_type):
    assert collection_id == TEST_COLLECTION_ID
    assert vector_size == TRANSFORMER_VECTOR_SIZE
    assert distance_type == DISTANCE_METRIC
    return OK_REPONSE


def mock_insert_embeddings(
    _, collection_id, embeddings, words, definitions, pos=[], example=[]
):
    assert collection_id == TEST_COLLECTION_ID
    assert numpy.isclose(embeddings[0][0], 0.06030972, atol=1e-04)
    assert words[0] == "tricksy"
    assert definitions[0] == "marked by skill in deception"
    return OK_REPONSE


def mock_create_collection_alt(_, collection_id, vector_size, distance_type):
    assert collection_id == TEST_COLLECTION_ID
    assert vector_size == ALT_VECTOR_SIZE
    assert distance_type == ALT_DISTANCE_METRIC
    return OK_REPONSE


def mock_insert_embeddings_alt(
    _, collection_id, embeddings, words, definitions, pos=[], example=[]
):
    assert collection_id == TEST_COLLECTION_ID
    assert numpy.isclose(embeddings[0][0], -0.03384724, atol=1e-04)
    assert words[0] == "tricksy"
    assert definitions[0] == "marked by skill in deception"
    return OK_REPONSE


def test_populate_adds_data_default(mocker):
    mocker.patch("populate_db.DBConnector._create_collection", mock_create_collection)
    mocker.patch("populate_db.DBConnector.insert_embeddings", mock_insert_embeddings)
    populate(2, TEST_COLLECTION_ID, test=True)


def test_populate_adds_data_alt(mocker):
    mocker.patch(
        "populate_db.DBConnector._create_collection", mock_create_collection_alt
    )
    mocker.patch(
        "populate_db.DBConnector.insert_embeddings", mock_insert_embeddings_alt
    )
    populate(
        2,
        TEST_COLLECTION_ID,
        model_name=ALT_MODEL_NAME,
        vector_size=ALT_VECTOR_SIZE,
        distance_type=ALT_DISTANCE_METRIC,
        test=True,
    )
