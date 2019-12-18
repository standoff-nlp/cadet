from cadet_app.models import *
from iso639 import languages
from lxml import etree
from standoffconverter import Converter


SPACY_LANGS = [
    "af",
    "ar",
    "bg",
    "bn",
    "ca",
    "cs",
    "da",
    "de",
    "el",
    "en",
    "es",
    "et",
    "fa",
    "fi",
    "fr",
    "ga",
    "he",
    "hi",
    "hr",
    "hu",
    "id",
    "is",
    "it",
    "ja",
    "kn",
    "ko",
    "lb",
    "lt",
    "lv",
    "mr",
    "nb",
    "nl",
    "pl",
    "pt",
    "ro",
    "ru",
    "si",
    "sk",
    "sl",
    "sq",
    "sr",
    "sv",
    "ta",
    "te",
    "th",
    "tl",
    "tr",
    "tt",
    "uk",
    "ur",
    "vi",
    "xx",
    "zh",
]


def update_spacy_langs():
    for lang in SPACY_LANGS:
        try:
            name = languages.get(alpha2=lang)
            SpacyLanguage.objects.update_or_create(iso=lang, language=name.name)
        except KeyError:
            SpacyLanguage.objects.update_or_create(iso=lang)


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
    
    annotations = Annotation.objects.filter(project=project, text=text).order_by('start_char') 

    init_tree = etree.Element("root")
    init_tree.text = text.text

    cadet = Converter.from_tree(init_tree)

    for a in annotations:
        
        if not a.end_char:
            end_char = a.start_char + len(a.annotation_text)
        else:
            end_char = a.end_char            

        cadet.add_annotation(a.start_char,end_char, a.annotation_type.name, 0, {})

    result = etree.tostring(cadet.tree)
    return result




def add_annotations_with_beautifulsoup(text, project):
    """This was a function to add annotations with BeautifulSoup.  David Lassner created something far better, see add_annotations() above."""
    annotations = Annotation.objects.filter(project=project, text=text).order_by('start_char') 

    html = '<html></html'
    soup = BeautifulSoup(html)
    text = text.text
    first_span = text[:annotations.first().start_char]
    new_span = soup.new_tag('p') 
    new_span.string = first_span
    soup.html.insert(0, new_span)
    annotations_tuple = annotations.values_list('id','annotation_text','start_char','end_char', 'annotation_type__name') 
    for i, annotation in enumerate(annotations_tuple):
        if annotations_tuple[i][3] == 'token':
            new_span = soup.new_tag('a', href='#', id=annotations_tuple[i][0], **{'class':annotations_tuple[i][4]})
            new_span.string = annotations_tuple[i][1]
            soup.html.insert(i, new_span)
            text_span = soup.new_tag('p')
            if not annotations_tuple[i][3]:
                end_char = annotations_tuple[i][2] + len(annotations_tuple[i][1])
            else:
                end_char = annotations_tuple[i][3]

            text_span.string = text[annotation[i].end_char:annotation[i+1].start_char] 
            soup.html.insert(i, text_span)

            #add gap text
            # TODO stopped here,     
