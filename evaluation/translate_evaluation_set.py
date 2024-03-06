import json
import os

from translator import translate

# takes only first definition from topics dictionary


def trim_dictionary():
    data_file = open(
        "evaluation/topics_dictionary/topics_dictionary.json", encoding="utf8"
    )
    data = json.load(data_file)
    words = []
    definitions = []
    seen_words = set()
    for d in data:
        word = d["word"]
        if not (word in seen_words):
            words.append(word)
            definitions.append(d["definitions"])
            seen_words.add(word)

    data = []

    for i in range(len(words) - 1):
        data.append(
            {
                "word": words[i],
                "definitions": definitions[i],
            }
        )

    with open(
        "evaluation/trimmed_evaluation_set.json", "w", encoding="utf8"
    ) as outfile:
        json.dump(data, outfile, indent=4)


# translates definitions between indices n_translations times and populates translation_evaluation_set.json


def populate(start_index, end_index, n_translations):
    data_file = open("evaluation/trimmed_evaluation_set.json", encoding="utf8")
    output_file = (
        "evaluation/translated_evaluation_set_"
        + str(start_index)
        + "-"
        + str(end_index - 1)
        + ".json"
    )
    data = json.load(data_file)
    words = []
    definitions = []

    for i in range(start_index, end_index):
        words.append(data[i]["word"])
        definitions.append(data[i]["definitions"])

    translated_definitions = translate(definitions, n_translations)
    data = []

    for i in range(end_index - start_index):
        data.append(
            {
                "word": words[i],
                "definitions": definitions[i],
                "translated_definitions": translated_definitions[i],
            }
        )
    with open(output_file, "w", encoding="utf8") as outfile:
        json.dump(data, outfile, indent=4)


populate(200, 210, 5)
