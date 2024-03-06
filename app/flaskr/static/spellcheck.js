var dictionary = new Typo("en_US", false, false, { dictionaryPath: "static/typo" });

function isLetter(c) {
    return c.toLowerCase() != c.toUpperCase();
}

function hasNumber(myString) {
    return /\d/.test(myString);
}

// Get suggestion for misspelled word. If no suggestion found, return the given word
function suggestWord(word) {
    const suggestions = dictionary.suggest(word);
    var suggestion = word;
    // Check if suggestions exist, is non empty and doesn't have number
    if (Array.isArray(suggestions) && suggestions.length && !hasNumber(suggestions[0])) {
        // Pick first suggested word
        suggestion = suggestions[0];
    }
    return suggestion;
}

// If no misspelled word detected, returns an empty string, otherwise tries to
// replace every misspelled word with the closest correctly spelled one.
export function spellcheck(definition) {

    var result = "";
    var misspelled = false;
    var word = "";
    var in_word = false;

    // Remove extra spaces
    const definition_trimmed = definition.replace(/\s+/g, ' ').trim();

    for (var i = 0; i < definition_trimmed.length; i++) {
        var c = definition_trimmed[i];
        // Check ' for can't don't, ...
        if (isLetter(c) || c == "'") {
            if (!in_word) {
                in_word = true;
            }
            word = word.concat(c);
        }
        // Not part of a word
        else {
            if (in_word) {
                in_word = false;
                if (!dictionary.check(word)) {
                    word = suggestWord(word);
                    misspelled = true;
                }
                result = result.concat(word);
                word = "";
            }
            result = result.concat(c);
        }
    }
    if (in_word) {
        if (!dictionary.check(word)) {
            word = suggestWord(word);
            misspelled = true;
        }
        result = result.concat(word);
    }
    if (misspelled) {
        return result;
    }
    return "";
}
