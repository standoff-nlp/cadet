from cadet_app.models import *
from iso639 import languages
from lxml import etree
from standoffconverter import Converter
from pathlib import Path
import spacy 

SPACY_LANGS = [] 
spacy_path = Path(spacy.__file__.replace('__init__.py',''))
spacy_langs = spacy_path / 'lang'
langs = [x for x in spacy_langs.iterdir() if x.is_dir()]
[SPACY_LANGS.append(str(lang).split('/')[-1]) for lang in langs if not str(lang).split('/')[-1] == '__pycache__']


def update_spacy_langs():
    for lang in SPACY_LANGS:
        try:
            name = languages.get(alpha2=lang)
            SpacyLanguage.objects.update_or_create(iso=lang, language=name.name, is_core=True)
        except KeyError:
            SpacyLanguage.objects.update_or_create(iso=lang, language='Multilingual', is_core=True)


def make_dict(**args):  # Used to create a dictionary of the current state
    return args


def update_state(request):
    request.session["query"] = request.POST.get("query", None)
    request.session["project"] = request.POST.get("project", None)
    request.session["text"] = request.POST.get("text", None)
    request.session["sentence"] = request.POST.get("sentence", None)
    request.session["token"] = request.POST.get("token", None)


def get_state(request):
    query = request.session.get("query")
    people = request.session.get("project")
    places = request.session.get("text")
    keywords = request.session.get("sentence")
    start_year = request.session.get("token")

    state = make_dict(*args)
    return state


def matcher(text, term, label):
    index = 0
    matches = []
    while True:
        index = text.find(term, index + 1)
        matches.append((index, index + len(term), label))
        if index == -1:
            break

    return matches[:-1]


def add_annotations(text, project):

    annotations = Annotation.objects.filter(project=project, text=text).order_by(
        "start_char"
    )

    init_tree = etree.Element("p")
    init_tree.text = text.text

    cadet = Converter.from_tree(init_tree)

    for a in annotations:

        if not a.end_char:
            end_char = a.start_char + len(a.annotation_text)
        else:
            end_char = a.end_char

        cadet.add_annotation(
            a.start_char,
            end_char,
            "a",
            0,
            {
                "id": str(a.pk),
                "class": a.annotation_type.name,
                "onclick": "select_annotation(this)",
            },
        )

    result = etree.tostring(cadet.tree)
    return result.decode("utf-8")


def export_tei(text, project):

    annotations = Annotation.objects.filter(project=project, text=text).order_by(
        "start_char"
    )

    init_tree = etree.Element("p")
    init_tree.text = text.text

    cadet = Converter.from_tree(init_tree)

    for a in annotations:

        if not a.end_char:
            end_char = a.start_char + len(a.annotation_text)
        else:
            end_char = a.end_char

        cadet.add_annotation(
            a.start_char, end_char, a.annotation_type.name, 0, {"id": str(a.pk),}
        )

    result = etree.tostring(cadet.tree)
    return result.decode("utf-8")

def get_previous_and_next_text(project_id, text):
    project_texts = list(Text.objects.filter(projects__id=project_id).values_list('text_slug', flat=True))
    
    for item in project_texts:
        if item == text:
            current = item
            print('current is', current)

    # find index in list for current
    index_current = project_texts.index(current)
    previous_text = project_texts[index_current - 1]
    try:
        next_text = project_texts[index_current + 1]
    except:
        next_text = project_texts[0]
    return previous_text, next_text