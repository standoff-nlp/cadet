from django.shortcuts import render, get_object_or_404, redirect
from collections import Counter
from cadet_app.models import Project, Text
from pathlib import Path
from django.conf import settings
import spacy


def make_scored_spans(request, sequence_length):
    """This is a utility function used to generate a sorted list of spans for annotation.
    To save resources, the function is run once and then saved to session, rather than
    every time the page is loaded
    returns: a list of spaCy span objects sorted by score. For each token in the span, a score is given 
    based on the frequency of the token in the corpus. The span score is the sum of all the token scores 
    in the span. 
    """

    project = get_object_or_404(Project, id=request.session.get("project_id"))
    texts = Text.objects.filter(projects=project)
    text = "".join([text.text for text in texts])

    project_language = project.spacy_language.slug.replace('-','_')
    model_path = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/models/' + project_language )
    if model_path.exists():
        try:
            nlp = spacy.load(str(model_path))
        except:
            lang = spacy.util.get_lang_class(project_language)
            nlp = lang()

    else:
        lang = spacy.util.get_lang_class(project_language)
        nlp = lang()
    
    doc = nlp(text)
    # https://stackoverflow.com/questions/37253326/how-to-find-the-most-common-words-using-spacy
    words = [token.text for token in doc if token.is_stop != True and token.is_punct != True]
    word_freq = dict(Counter(words))

    # split the doc into equal spans for sorting https://stackoverflow.com/questions/13673060/split-string-into-strings-by-length
    spans = [doc[i:i+sequence_length] for i in range(0, len(doc), sequence_length)]
    #count common terms, unique terms, 
    def word_score(word:str):
        if word in word_freq.keys():
            score = word_freq[word]
        else:
            score = 0
        return score

    # calculate span scores
    scored_spans = {}    
    for span in spans:
        scored_spans[span.text] = 0
        for token in span:
            scored_spans[span.text] += word_score(token.text)

    return scored_spans # Because session saves this data to JSON, we sort the scored spans in the view
    

def strategic(request, project, text):
    context = {}
    if not request.session.get("scored_spans"):
        scored_spans = make_scored_spans(request, 10) #TODO, if needed, add slider to change span length
    else:
        scored_spans = request.session.get("scored_spans") 

    sorted_spans  = {k: v for k, v in sorted(scored_spans.items(), key=lambda item: item[1], reverse=True)}
    #context['sorted_spans'] = [span.text for span in sorted_scored_spans.keys()]
    print(sorted_spans)
    context['sorted_spans'] = sorted_spans

    return render(request, "strategic.html", context)