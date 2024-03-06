import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import json

# Script to remove duplicates


def clean(data):
    clean_data_dict = {}

    for obj in data:
        clean_data_dict[(obj["definitions"], obj["word"])] = obj

    clean_data = list(clean_data_dict.values())
    return json.dumps(clean_data, indent=4, separators=(",", ": "))


if __name__ == "__main__":
    data_file = open("population/dictionary_data.json")
    data = json.load(data_file)
    clean_data_string = clean(data)
    with open("population/dictionary_data_clean.json", "w") as clean_data_file:
        clean_data_file.write(clean_data_string)
