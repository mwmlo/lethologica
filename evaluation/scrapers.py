import csv
import json
import os
import urllib

import html2text
import requests
from requests.adapters import HTTPAdapter, Retry

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOPIC_FILES_DIR = os.path.join(SCRIPT_DIR, "topics_dictionary", "topic_files")
TOPICS = ["drum", "education", "emotion", "hunt", "technology"]
JSON_PREFIX = "topics_dictionary_"
JSON_SUFFIX = "_manual.json"
TXT_SUFFIX = ".txt"

# change SOLUTION_NAME to change which reverse dictionary is used
SOLUTION_NAME = "reversedictionary.org"  # "onelook.com"

CSV_PATH = os.path.join(SCRIPT_DIR, "onelook_csvs")
CSV_SUFFIX = "_onelook.csv"

if SOLUTION_NAME == "reversedictionary.org":
    CSV_PATH = os.path.join(SCRIPT_DIR, "reversedict_csvs")
    CSV_SUFFIX = "_reversedict.csv"


# scrape reversedictionary.org, returning a list of found words ordered by score
def scrape_reversedict(session, definition):
    response = session.get(
        "https://reversedictionary.org/wordsfor/" + urllib.parse.quote(definition)
    )
    response_text = response.text
    if not response.text:
        print("no response")
        return []
    # crop the text up to the ',"terms":' part
    words_json = response_text.split(',"terms":')[1].split("}</script>")[0]

    words = []

    for word in json.loads(words_json):
        words.append(word["word"])

    return words


# scrape onelook.com/thesaurus, returning a list of found words ordered by score
def scrape_onelook(session, definition):
    response = session.get(
        "https://www.onelook.com/api/words?ml="
        + urllib.parse.quote(definition)
        + "&qe=ml&md=dpfcy&max=200&rif=1&k=olthes_r4"
    )
    if not response.text:
        print("no response")
        return []
    response_text = response.text
    # crop the text up to the ',"terms":' part
    words_json = json.loads(response_text)[1:]
    words = []

    for word in words_json:
        words.append(word["word"])

    return words


if __name__ == "__main__":
    # file to write to
    with open(
        os.path.join(CSV_PATH, "alt_dictionary" + CSV_SUFFIX), "w", newline=""
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["model name", "word", "test set definition", "ranking"])

        test_words = []
        # file to read from
        with open(os.path.join(SCRIPT_DIR, "topics_alt_dictionary.json"), "r") as file:
            test_words = json.load(file)
            file.close()

        s = requests.Session()

        retries = Retry(
            total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )
        s.mount("https://", HTTPAdapter(max_retries=retries))
        for word in test_words:
            ranking = -1
            responses = []
            if SOLUTION_NAME == "onelook.com":
                responses = scrape_onelook(s, word["definitions"])
            else:
                responses = scrape_reversedict(s, word["definitions"])
            print(word["word"], "\t\t\t", responses[:3])
            if word["word"] in responses:
                ranking = responses.index(word["word"]) + 1

            writer.writerow([SOLUTION_NAME, word["word"], word["definitions"], ranking])

        file.close()
