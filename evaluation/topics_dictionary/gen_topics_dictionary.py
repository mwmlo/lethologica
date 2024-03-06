import argparse
import json
import os

import requests

DICTIONARY_DATA_PATH = "evaluation/english_wordnet/english_wordnet_clean.json"
TOPICS_DICTIONARY_DIR = "evaluation/topics_dictionary"
TOPIC_FILES_DIR = os.path.join(TOPICS_DICTIONARY_DIR, "topic_files")
TOPICS_DICTIONARY_PATH = os.path.join(TOPICS_DICTIONARY_DIR, "topics_dictionary.json")
TOPICS_ALT_DICTIONARY_PATH = os.path.join(
    TOPICS_DICTIONARY_DIR, "topics_alt_dictionary.json"
)

DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"
HTTP_OK = 200


# create a topics dictionary containing entries of words given in a list of topic files
def create_topics_dictionary(topic_files, dictionary_data):
    # collate all words to enter the topics dictionary
    topics_word_set = set()
    for topic_file in topic_files:
        with open(topic_file, "r") as f:
            word_list = f.read().splitlines()
            topics_word_set.update(word_list)

    # map each word to False, indicating that no entry has yet been accessed for that word in the dictionary data
    topics_word_map = {word: False for word in topics_word_set}

    # create the topics dictionary
    topics_dictionary = []

    if dictionary_data == "api":
        for word in topics_word_set:
            # get the definition from dictionaryapi.dev
            r = requests.get(DICTIONARY_API_URL + word)
            if r.status_code == HTTP_OK:
                body = r.json()
                temp_defs = []
                for result in body:
                    for m in result["meanings"]:
                        for d in m["definitions"]:
                            temp_defs.append(d["definition"])

                if len(temp_defs) > 0:
                    chosen_def = user_choose(temp_defs, word)
                    topics_dictionary.append({"word": word, "definitions": chosen_def})
                    topics_word_map[word] = True

    else:
        # in default mode, get definitions from the JSON
        for entry in dictionary_data:
            # check if the dictionary entry should be added to the topics dictionary
            if entry["word"] in topics_word_map:
                # update the word map's boolean to indicate this word has been found in the dictionary data
                topics_word_map[entry["word"]] = True
                # add the dictionary entry to the topics dictionary
                topics_dictionary.append(entry)

    # print all words that were part of the topics word set, but not found in the dictionary data
    unaccessed_words = [
        word for word, accessed in topics_word_map.items() if not accessed
    ]
    if len(unaccessed_words) > 0:
        print("The following words were not found: ", unaccessed_words)

    # save the topics dictionary as a .json file
    if dictionary_data == "api":
        with open(TOPICS_ALT_DICTIONARY_PATH, "w") as f:
            json.dump(topics_dictionary, f, indent=2)
    else:
        with open(TOPICS_DICTIONARY_PATH, "w") as f:
            json.dump(topics_dictionary, f, indent=2)


# given a list of definitions, prompt the user to manually choose
def user_choose(defs_list, word):
    if len(defs_list) == 1:
        return defs_list[0]

    print("CHOOSE DEFINITION:", word)
    for i in range(0, len(defs_list)):
        print(i, ": ", defs_list[i])

    # await valid user input
    chosen = False
    i = 0

    while not chosen:
        i = int(input("Accept which definition?   "))
        if i < 0 or i >= len(defs_list):
            print(i, " outside of range.")
        else:
            chosen = True

    os.system("cls||clear")

    return defs_list[i]


if __name__ == "__main__":
    # get the paths of all files in the topic files directory
    add_path_suffix = lambda filename: os.path.join(TOPIC_FILES_DIR, filename)
    topic_file_paths = list(map(add_path_suffix, os.listdir(TOPIC_FILES_DIR)))

    # parse the arguments: a list of .txt topic files from which to extract words to enter the topics dictionary
    # if no arguments have been passed, by default all files in the topic files directory are used
    parser = argparse.ArgumentParser(
        description="""Process words from topic files into a combined topics dictionary.
                       Each topic file is a .txt file containing a list of newline-separated words to enter the topics dictionary."""
    )
    parser.add_argument(
        "topic_files",
        nargs="*",
        default=topic_file_paths,
        help="List of .txt topic files from which to extract words to enter the topics dictionary",
    )
    parser.add_argument("--altdict", action="store_true")
    args = parser.parse_args()

    # load the dictionary data
    with open(DICTIONARY_DATA_PATH, "r") as file:
        dictionary_data = json.load(file)

    if args.altdict:
        dictionary_data = "api"

    # create the topics dictionary using the given topic files and dictionary data
    create_topics_dictionary(args.topic_files, dictionary_data)

    # print the topic files used to create the combined topics dictionary
    print(
        "Created topics dictionary from the following topic files: ", args.topic_files
    )
