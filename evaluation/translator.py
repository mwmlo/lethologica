import random

from deep_translator import GoogleTranslator

# translates input_str in english to a random language n times, returns the resulting string in english


def translate(to_translate, n):
    translated = to_translate
    previous_lang = "english"
    langs_dict = GoogleTranslator().get_supported_languages(as_dict=True)
    langs_list = list(langs_dict.keys())

    for i in range(n):
        # to make sure the language translated to is different from the current language, previous_lang is removed
        lang = random.choice([x for x in langs_list if x != previous_lang])
        code = langs_dict[lang]
        translated = GoogleTranslator(
            source=langs_dict[previous_lang], target=code
        ).translate_batch(translated)
        previous_lang = lang

    # translate back to english
    translated = GoogleTranslator(
        source=langs_dict[previous_lang], target="en"
    ).translate_batch(translated)

    return translated
