# Lethologica

## Getting started

Set up a virtual environment and install Flask:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install Flask
```

Run the Flask application: `python -m flask --app app/flaskr run`
However the real deployed start point is: `python -m flask --app app/flaskr/__init__ run`

## Environment variables

To use SemaDB, you need to create a `.env` file in the root repository.
In the `.env` file, add your RapidAPI keys for SemaDB.

Also add your CSRF secret key.

```bash
API_KEY_PROD=your_production_api_key
API_KEY_TEST=your_test_api_key
APP_SECRET=CSRF_secret_key
```

The `.env` file should NOT be committed to GitLab to protect the API key.

## Running tests

`python3 -m pytest`

## Run pre-commit hook

`pre-commit run --all-files `

## Populate the database

`python3 database.populate_db.py`

## Credits

The dataset for reverse dictionary searches is based on definitions from Open English WordNet and Wikitionary.

**Open English WordNet** is derived from [Princeton WordNet](http://wordnet.princeton.edu/) by the Open English WordNet Community and released under the [Creative Commons Attribution (CC-BY) 4.0 License](https://creativecommons.org/licenses/by/4.0/).

John P. McCrae, Alexandre Rademaker, Francis Bond, Ewa Rudnicka and Christiane Fellbaum (2019) [English WordNet 2019 – An Open-Source WordNet for English](https://aclanthology.org/2019.gwc-1.31/). In *Proceedings of the 10th Global WordNet Conference – GWC 2019*, Wrocław

**Wiktionary**: Definitions and other text are available under the [Creative Commons Attribution-ShareAlike License](https://creativecommons.org/licenses/by-sa/4.0/); additional terms may apply.

The spellchecker dictionary is based on a subset of the original English wordlist created by Kevin Atkinson for Pspell and  Aspell and thus is covered by his original LGPL license.  The affix file is a heavily modified version of the original english.aff file which was released as part of Geoff Kuenning's Ispell and as such is covered by his BSD license.As used in the typo-js library [here](https://github.com/cfinke/Typo.js/tree/master/typo/dictionaries/en_US).
