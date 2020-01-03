import spacy
from django.conf import settings
from pathlib import Path

#spacy_path = Path(spacy.__file__.replace('__init__.py',''))
#spacy_lang = spacy_path / 'lang'

def create_custom_spacy_language_object(language):
    path = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/lang/' + language)
    path.mkdir(parents=False, exist_ok=False)
    spacy_path = Path(spacy.__file__.replace('__init__.py',''))
    spacy_lang = spacy_path / 'lang' / language
    spacy_lang.symlink_to(path)
    init = path / '__init__.py'
    with init.open('w', encoding="utf-8") as f: 
        f.write(
f"""
from spacy.lang.{language}.stop_words import STOP_WORDS

# These files are part of spaCy and do not need to be edited
from spacy.lang.tokenizer_exceptions import BASE_EXCEPTIONS
from spacy.lang.norm_exceptions import BASE_NORMS
from spacy.language import Language
from spacy.attrs import LANG, NORM
from spacy.util import update_exc, add_lookups


# https://spacy.io/usage/adding-languages#language-subclass
class {language}Defaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "{language}"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS,
    )
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS,)
    stop_words = STOP_WORDS


class {language}(Language):
    lang = "{language}"
    Defaults = {language}Defaults


__all__ = ["{language}"]
""")

    stop = path / 'stop_words.py'
    with stop.open('w', encoding="utf-8") as f:
        f.write(
f'''
# coding: utf8
from __future__ import unicode_literals


STOP_WORDS = set(
    """
""".split()
)
''')