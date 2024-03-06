import json
import os
from dataclasses import dataclass
from math import floor

import numpy as np
from flask import Blueprint, Flask, render_template, request
from flask_wtf.csrf import CSRFError

from database.db_connector import DBConnector

PROD_COLLECTION_ID = "lethoData"
HTTP_OK = 200
FORBIDDEN_ERR = 403

app = Flask(__name__)
home_page = Blueprint("my_view", __name__)

# colors and score thresholds for score display
colors = {
    "red": "ed8977",
    "orange": "edb877",
    "yellow": "eded77",
    "green": "77ed8b",
    "blue": "77ede9",
}

thresholds = {
    "red": 0,
    "orange": 70,
    "yellow": 75,
    "green": 80,
    "blue": 90,
}

# get common words from json
common_words_filename = os.path.join(app.root_path, "static", "common_words.json")
with open(common_words_filename, "r") as common_words_file:
    common_words = json.load(common_words_file)["commonWords"]

# score for cosine distance is 0 (for very close) and 2 (for very far)


def convert_score(score):
    return 100 - floor(score / 2 * 100)


@dataclass
class Result:
    word: str
    score: int
    defEx: list
    pos: str
    common: bool


@home_page.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template("csrf_error.html", reason=e.description), FORBIDDEN_ERR


DEFAULT_RESULTS = [Result("", -1, [("", "")], "", False)]


@home_page.route("/", methods=["POST", "GET"])
def home():
    results = []
    query = None
    spellchecked = None
    if not request.form:
        results = DEFAULT_RESULTS
    else:
        query = request.form["def"]
        if query == "":
            results = DEFAULT_RESULTS
        else:
            embedding = request.form["embedding_input"]
            spellchecked = request.form["spellchecked_input"]
            embedding = json.loads(embedding)
            embedding = np.asarray(list(embedding["data"].values()))
            # Get similar definitions
            db_connector = DBConnector()
            response = db_connector.get_matches(
                collection_id=PROD_COLLECTION_ID, target_embedding=embedding, limit=50
            )
            # result dict: maps word and part of speech to dictionary of definitions, each mapped to a score and example
            duplicate_removal_result = {}
            if response.status_code == HTTP_OK:
                for match in response.json()["points"]:
                    metadata = match["metadata"]
                    key = (metadata["word"], metadata["pos"])
                    # check if same word and part of speech is already in dictionary
                    if key not in duplicate_removal_result:
                        # word and part of speech not in dictionary, create new entry
                        duplicate_removal_result[key] = {
                            metadata["def"]: (
                                convert_score(match["distance"]),
                                metadata["ex"],
                            )
                        }
                    elif metadata["def"] not in duplicate_removal_result[key]:
                        # word, part of speech with given definition not already present, add it
                        duplicate_removal_result[key][metadata["def"]] = (
                            convert_score(match["distance"]),
                            metadata["ex"],
                        )
                for key, defDict in duplicate_removal_result.items():
                    (word, pos) = key
                    score = -1
                    defEx = []  # list of (definition, example) tuples
                    for definition, meta in defDict.items():
                        score = max(
                            score, meta[0]
                        )  # score is the maximum of all scores
                        defEx.append((definition, meta[1]))
                    results.append(
                        Result(word, score, defEx, pos, word in common_words)
                    )

    return render_template(
        "home.html",
        query=query,
        results=results,
        colors=colors,
        thresholds=thresholds,
        spellchecked=spellchecked,
    )
