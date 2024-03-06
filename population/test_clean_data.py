from clean_data import clean


def test_cleaning_removes_pure_duplicates():
    data = [
        {
            "word": "tricksy",
            "lexnames": ["adj.all"],
            "root_affix": ["y"],
            "sememes": ["sly"],
            "definitions": "marked by skill in deception",
        },
        {
            "word": "worshipful",
            "lexnames": ["adj.all"],
            "root_affix": ["ful"],
            "sememes": ["glorious"],
            "definitions": "showing great reverence for god",
        },
        {
            "word": "tricksy",
            "lexnames": ["adj.all"],
            "root_affix": ["y"],
            "sememes": ["sly"],
            "definitions": "marked by skill in deception",
        },
    ]
    expected = """[
    {
        "word": "tricksy",
        "lexnames": [
            "adj.all"
        ],
        "root_affix": [
            "y"
        ],
        "sememes": [
            "sly"
        ],
        "definitions": "marked by skill in deception"
    },
    {
        "word": "worshipful",
        "lexnames": [
            "adj.all"
        ],
        "root_affix": [
            "ful"
        ],
        "sememes": [
            "glorious"
        ],
        "definitions": "showing great reverence for god"
    }
]"""
    actual = clean(data)
    assert actual == expected


def test_cleaning_allows_two_words_with_duplicate_defintions():
    data = [
        {
            "word": "tricksy",
            "lexnames": ["adj.all"],
            "root_affix": ["y"],
            "sememes": ["sly"],
            "definitions": "marked by skill in deception",
        },
        {
            "word": "deceitful",
            "lexnames": ["adj.all"],
            "root_affix": ["y"],
            "sememes": ["sly"],
            "definitions": "marked by skill in deception",
        },
    ]
    expected = """[
    {
        "word": "tricksy",
        "lexnames": [
            "adj.all"
        ],
        "root_affix": [
            "y"
        ],
        "sememes": [
            "sly"
        ],
        "definitions": "marked by skill in deception"
    },
    {
        "word": "deceitful",
        "lexnames": [
            "adj.all"
        ],
        "root_affix": [
            "y"
        ],
        "sememes": [
            "sly"
        ],
        "definitions": "marked by skill in deception"
    }
]"""
    actual = clean(data)
    assert actual == expected
