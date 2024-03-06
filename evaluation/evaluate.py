import argparse
import csv
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from database.db_connector import DBConnector
from database.local_db import create_local_db
from transformer.transformer import Transformer

HTTP_OK = 200

model_collections = {
    "allminilm": "all-MiniLM-L6-v2",
    "allmpnet": "all-mpnet-base-v2",
    "alldistilroberta": "all-distilroberta-v1",
    "mqadistilbert": "multi-qa-distilbert-cos-v1",
    "paraphrasempnet": "paraphrase-multilingual-mpnet-base-v2",
    "distiluse": "distiluse-base-multilingual-cased-v1",
    "paraphrase-fast": "paraphrase-MiniLM-L3-v2",
    "MQADall": "multi-qa-distilbert-cos-v1",  # Chosen model
    "MQADwordnet": "multi-qa-distilbert-cos-v1",
    "MqadWikWordnet": "multi-qa-distilbert-cos-v1",  # Expanded DB
    "lethoData": "multi-qa-distilbert-cos-v1",  # Expanded DB, punctuation removed
}

db_connector = DBConnector()


def run_eval(test_set_file_path, collection_id, distance_metric):
    set_name = re.findall(r"[^\/]+(?=\.)", test_set_file_path)[0]
    test_set_file = open(test_set_file_path)
    test_set_data = json.load(test_set_file)
    write_eval_results(
        file_name=f"eval_{collection_id}_{set_name}_{distance_metric}.csv",
        test_set_data=test_set_data,
        collection_id=collection_id,
        distance_metric=distance_metric,
    )
    test_set_file.close()


def write_eval_results(file_name, test_set_data, collection_id, distance_metric):
    # Appends to file, creates new file if it doesn't exist
    with open(file_name, "a", newline="") as file:
        writer = csv.writer(file)
        field = ["model name", "word", "test set definition", "ranking"]
        writer.writerow(field)

        compare_models(
            test_set_data=test_set_data, collection_id=collection_id, writer=writer
        )

        file.close()


# Takes in a JSON for test_set
def compare_models(test_set_data, collection_id, writer):
    model_name = model_collections[collection_id]
    encoder = Transformer(model_name)
    # Check through words in test set
    for word_def in test_set_data:
        target_word = word_def["word"]
        definition = word_def["definitions"]
        if "translated_definitions" in word_def:
            definition = word_def["translated_definitions"]
        # Encode query and get similar definitions
        embedding = encoder.encode(definition)
        response = db_connector.get_matches(
            collection_id=collection_id, target_embedding=embedding
        )
        if response.status_code is not HTTP_OK:
            raise Exception(f"Error connecting to DB: {response.json()}")
        # Record ranking
        ranking = -1
        for i, match in enumerate(response.json()["points"]):
            if target_word == match["metadata"]["word"]:
                ranking = i + 1
                break
        # Write to CSV
        writer.writerow([model_name, target_word, definition, ranking])


def run_local_eval(test_set_path, collection_id, local_db):
    set_name = re.findall(r"[^\/]+(?=\.)", test_set_path)[0]
    test_set_file = open(test_set_path)
    test_set_data = json.load(test_set_file)
    test_set_file.close()

    csv_dest = f"localeval_{collection_id}_{set_name}_{local_db.distance_metric}.csv"
    csv_file = open(csv_dest, "w")
    writer = csv.writer(csv_file)
    field = ["model name", "word", "test set definition", "ranking"]
    writer.writerow(field)

    for word_def in test_set_data:
        # print("Word:", word_def["word"], ":", word_def["definitions"])
        definition = word_def["definitions"]
        if "translated_definitions" in word_def:
            definition = word_def["translated_definitions"]

        results = local_db.similarity_search(definition)

        ranking = -1
        if word_def["word"] in results:
            ranking = results.index(word_def["word"]) + 1

        writer.writerow(
            [
                model_collections[collection_id],
                word_def["word"],
                definition,
                ranking,
            ]
        )

    csv_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate evaluation CSV file using given test set file"
    )
    parser.add_argument(
        "--test_set",
        required=True,
        help="file path to JSON dictionary data",
    )
    parser.add_argument(
        "--collection_id",
        required=True,
        help="name of semadb collection",
    )
    parser.add_argument(
        "--distance_metric",
        required=True,
        help="cosine, dot or euclidean distance",
    )
    parser.add_argument(
        "--local",
        help="if set, creates a local db and evaluates on that",
        action="store_true",
    )
    args = parser.parse_args()

    if args.collection_id not in model_collections:
        raise Exception("Invalid collection ID.")

    if not args.local:
        print(
            f"Run evaluation for {args.collection_id} on {args.test_set} with {args.distance_metric} distance"
        )
        run_eval(
            test_set_file_path=args.test_set,
            collection_id=args.collection_id,
            distance_metric=args.distance_metric,
        )
    else:
        # create the local db from trimmed_evaluation_set.json
        with open("evaluation/trimmed_evaluation_set.json") as file:
            words_json = json.load(file)
            file.close()
            word_def_pairs = []
            for word in words_json:
                word_def_pairs.append((word["word"], word["definition"]))

            local_db = create_local_db(
                word_def_pairs,
                model_collections[args.collection_id],
                args.distance_metric,
            )
            run_local_eval(args.test_set, args.collection_id, local_db)
