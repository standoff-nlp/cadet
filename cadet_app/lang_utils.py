import spacy
from django.conf import settings
from pathlib import Path
from shutil import copyfile
from django.utils.text import slugify
from cadet_app.utils import blank_examples

#spacy_path = Path(spacy.__file__.replace('__init__.py',''))
#spacy_lang = spacy_path / 'lang'
def create_stop_words(path):
    path = path / 'stop_words.py'
    with path.open('w', encoding="utf-8") as f:
        f.write(
f'''
# coding: utf8
from __future__ import unicode_literals


STOP_WORDS = set(
    """
""".split()
)
''')

def create_examples(path):
    examples = path / 'examples.py'
    with examples.open('w', encoding="utf-8") as f: 
        f.write(blank_examples)

def create_spacy_language(language):
    language = slugify(language).replace('-','_')
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
class {language.capitalize()}Defaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "{language}"
    lex_attr_getters[NORM] = add_lookups(
        Language.Defaults.lex_attr_getters[NORM], BASE_NORMS,
    )
    tokenizer_exceptions = update_exc(BASE_EXCEPTIONS,)
    stop_words = STOP_WORDS


class {language.capitalize()}(Language):
    lang = "{language}"
    Defaults = {language.capitalize()}Defaults


__all__ = ["{language.capitalize()}"]
""")

    create_stop_words(path)
    create_examples(path)
   
# still needs creation of lookups path 


def clone_spacy_language(language, clone):
    language = slugify(language).replace('-','_')
    new_path = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/lang/' + language)
    new_path.mkdir(parents=False, exist_ok=False)
    
    # Create symlink between spacy/lang and the new custom languages directory
    lang_path = Path(spacy.__file__.replace('__init__.py','')) / 'lang' / language
    lang_path.symlink_to(new_path)
    if clone.is_core:
        core_path = Path(spacy.__file__.replace('__init__.py','')) / 'lang' / clone.iso
        assert core_path.exists()
    else:
        core_path = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/lang/' + clone.language)
        assert core_path.exists()

    # copy files from core to custom 
    core_files = [x for x in core_path.glob('**/*') if x.is_file() and 'pyc' not in str(x)]
    for src in core_files:
        dest = new_path / src.name  
        copyfile(src, dest)

    # Edit imports and variable names
    
    language_name = spacy.util.get_lang_class(clone.iso).__name__
    init = new_path / '__init__.py'
    init_text = init.read_text()
    init_text = init_text.replace(language_name, language.capitalize()).replace('"'+clone.iso+'"','"'+language+'"') # quotes added to avoid false matches
    init_text = init_text.replace('from ...', 'from spacy.')
    init_text = init_text.replace('from ..', 'from spacy.lang.')
    init_text = init_text.replace('from .', 'from spacy.lang.' + language + '.')
    init.write_text(init_text)

    new_files = [x for x in new_path.glob('**/*') if x.is_file() and x.name != '__init__.py']
    for file in new_files:
        file_text = file.read_text()
        file_text = file_text.replace('from ...', 'from spacy.')
        file_text = file_text.replace('from ..', 'from spacy.lang.')
        file_text = file_text.replace('from .', 'from spacy.lang.' + language + '.')
        file.write_text(file_text)

    #spacy lookups ~ using pip install spacy[lookups]
    import spacy_lookups_data
    spacy_lookups = Path(spacy_lookups_data.__file__.replace('__init__.py','')) / 'data'
    assert spacy_lookups.exists()

    # Use the iso code to identify lookups-data files 
    new_lookups = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/lookups-data/')
    lookups_files = [x for x in spacy_lookups.glob('**/*') if x.is_file() and clone.iso+'_' in str(x)]
    for src in lookups_files:
        new_name = src.name.replace(clone.iso, language)
        dest = new_lookups / new_name
        copyfile(src, dest)

    # TODO copy lookups tests
        