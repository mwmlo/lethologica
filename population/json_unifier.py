import json

# transform a '\n' separated list of words and a list of definitions
# into a single entry for each word-definition pair
# and output as a single json file

INPUT_FILE_PATH = "evaluation/english_wordnet/wordnet_expanded_detailed.json"
OUTPUT_FILE_PATH = "population/wiknet_detailed_unified.json"

word_defs = []
with open(INPUT_FILE_PATH) as input_file:
    for line in input_file:
        word = json.loads(line)

        definitions = set()
        for definition in word["definitions"]:
            definitions.add(definition.strip(",;.: \n"))

        if word["word"] == "screening":
            print(definitions)

        for definition in definitions:
            word_defs.append(
                {
                    "word": word["word"],
                    "definitions": definition,
                    "part_of_speech": word["part_of_speech"],
                    "example": word["example"],
                }
            )
    input_file.close()

with open(OUTPUT_FILE_PATH, "w") as output_file:
    json.dump(word_defs, output_file, indent=2)
