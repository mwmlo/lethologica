import argparse
import json
import os
import sys

from database.db_connector import DBConnector
from transformer.transformer import Transformer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))


# Script to populate the database
DEFAULT_MODEL = "multi-qa-distilbert-cos-v1"
DEFAULT_DISTANCE = "cosine"
DEFAULT_VECTOR_SIZE = 768
LOG_FILE = "population/populate_db.log"
WORDS_IN_PAYLOAD = 500


def populate(
    num_words,
    collection_id,
    start_index=0,
    source="population/dictionary_data_clean.json",
    model_name=DEFAULT_MODEL,
    vector_size=DEFAULT_VECTOR_SIZE,
    distance_type=DEFAULT_DISTANCE,
    test=False,
):
    with open(LOG_FILE, "w") as log_file:
        log_file.write(f"Populating DB\n")
    connector = DBConnector(test=test)
    encoder = Transformer(model_name)
    # Create a collection, if it does not already exist
    response = connector._create_collection(
        collection_id=collection_id,
        vector_size=vector_size,
        distance_type=distance_type,
    )
    if response.status_code == 200:
        print("Created new collection:", collection_id, vector_size, distance_type)
    elif response.status_code == 409:
        print("Collection already exists")
    else:
        print("Could not create collection:", response.json())
        return
    # Open data file
    data_file = open(source)
    data = json.load(data_file)
    # Populate with a subset of samples (500 at a time)
    while start_index < num_words:
        words = []
        definitions = []
        parts_of_speech = []
        examples = []
        # Loop through dictionary 500 words at a time, until limit reached.
        range_index = min(min(start_index + WORDS_IN_PAYLOAD, num_words), len(data))

        for i in range(start_index, range_index):
            words.append(data[i]["word"])
            definitions.append(data[i]["definitions"])
            pos = data[i]["part_of_speech"] if "part_of_speech" in data[i] else ""
            parts_of_speech.append(pos)
            ex = data[i]["example"] if "example" in data[i] else ""
            examples.append(ex)

        # Embed and insert
        embeddings = encoder.encode(definitions)
        response = connector.insert_embeddings(
            collection_id=collection_id,
            embeddings=embeddings,
            words=words,
            definitions=definitions,
            pos=parts_of_speech,
            example=examples,
        )
        if response.status_code != 200:
            print(response.json())
        log_msg = f"Inserted index range [{start_index}, {range_index}) into collection. STATUS: {response.status_code}"
        start_index = range_index
        with open(LOG_FILE, "a") as log_file:
            log_file.write(log_msg + "\n")
        print(log_msg)
    data_file.close()


if __name__ == "__main__":
    # Usage: python3 population/populate_db.py --num_words N --collection_id ID --source FILEPATH --model_name MODEL_NAME --distance_type DISTANCE --vector_size V
    parser = argparse.ArgumentParser(
        description="Create a new collection from given dictionary source, with specified encoding model and distance type."
    )
    parser.add_argument(
        "--num_words",
        required=True,
        type=int,
        help="first N words to populate collection with",
    )
    parser.add_argument("--collection_id", required=True, help="name of collection")
    parser.add_argument(
        "--source",
        required=False,
        default="population/dictionary_data_clean.json",
        help="file path to JSON dictionary data",
    )
    parser.add_argument(
        "--start_index",
        required=False,
        default=0,
        type=int,
        help="start index at which to populate collection",
    )
    parser.add_argument(
        "--model_name",
        required=False,
        default=DEFAULT_MODEL,
        help="name of transformer model for encoding sentence embeddings",
    )
    parser.add_argument(
        "--distance_type",
        required=False,
        default=DEFAULT_DISTANCE,
        help="distance metric: euclidean, cosine or dot",
    )
    parser.add_argument(
        "--vector_size",
        required=False,
        default=DEFAULT_VECTOR_SIZE,
        type=int,
        help="size of vector embeddings",
    )

    args = parser.parse_args()

    populate(
        num_words=args.num_words,
        collection_id=args.collection_id,
        start_index=args.start_index,
        source=args.source,
        model_name=args.model_name,
        distance_type=args.distance_type,
        vector_size=args.vector_size,
    )

    print(
        f"Populated collection {args.collection_id} with {args.num_words} words:",
        args.source,
        args.model_name,
        args.distance_type,
        args.vector_size,
    )
