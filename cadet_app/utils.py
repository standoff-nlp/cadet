from cadet_app.models import *
from iso639 import languages


SPACY_LANGS = [ 'af',
'ar',
'bg',
'bn',
'ca',
'cs',
'da',
'de',
'el',
'en',
'es',
'et',
'fa',
'fi',
'fr',
'ga',
'he',
'hi',
'hr',
'hu',
'id',
'is',
'it',
'ja',
'kn',
'ko',
'lb',
'lt',
'lv',
'mr',
'nb',
'nl',
'pl',
'pt',
'ro',
'ru',
'si',
'sk',
'sl',
'sq',
'sr',
'sv',
'ta',
'te',
'th',
'tl',
'tr',
'tt',
'uk',
'ur',
'vi',
'xx',
'zh',]

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
    request.session['query'] = request.POST.get('query', None)
    request.session['project'] = request.POST.get('project', None)
    request.session['text'] = request.POST.get('text', None)
    request.session['sentence'] = request.POST.get('sentence', None)
    request.session['token'] = request.POST.get('token', None)
    
def get_state(request):
    query = request.session.get('query')
    people = request.session.get('project')
    places = request.session.get('text')
    keywords = request.session.get('sentence')
    start_year = request.session.get('token')

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

def handle_uploaded_file(file, language, dataset):

    print(dataset)

    #nlp = load_base_language(language)
    if file.content_type == 'text/plain':
        #doc = nlp(file.read())
        pass

    if file.content_type == 'text/csv':
        #doc = nlp(file.read())
        return 'Dataset added successfully. Select datasets below or add another.'

    if file.content_type == 'xml/tei':
        # TODO use standoff converter to create text/sentence/tokens (same as above) and annotations. 
        pass

    if file.content_type == 'application/octet-stream': # CoNNL-U
        pass
    return "Have a nice day!"