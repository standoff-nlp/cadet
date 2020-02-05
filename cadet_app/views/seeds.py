from django.shortcuts import render, get_object_or_404, redirect
from collections import Counter
from cadet_app.models import Project, Text, Annotation
from pathlib import Path
from django.conf import settings
from django.db.models import Q
import spacy
from lxml import etree
from standoffconverter import Converter
from cadet_app.utils import matcher


def add_annotations_to_span(span, text, project):
    end_char = span.start_char+len(span.text)
    annotations = Annotation.objects.filter(project=project,text=text,start_char__gte=span.start_char,end_char__lte=end_char).order_by(
        "start_char"
    )  # I used Q when trying to get this to work, still needed? 
    assert len(annotations) > 0, f'The queryset is empty! {project},{text}, {span.start_char},{end_char}'# TODO something wrong wwiwth the query? returning none 
    
    init_tree = etree.Element("p")
    init_tree.text = span.text
    
    cadet = Converter.from_tree(init_tree)

    baseline = annotations.first().start_char
    for a in annotations:
        
        end_char = a.end_char

        cadet.add_annotation(
            a.start_char - baseline,
            end_char - baseline,
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
    
    #Calculate word frequences within the entire corpus of project texts
    corpus = "".join([text.text for text in texts])
    corpus_doc = nlp(corpus)
    corpus_words = [token.text for token in corpus_doc]
    word_freq = dict(Counter(corpus_words))


    def word_score(word:str):
        if word in word_freq.keys():
            score = word_freq[word]
        else:
            score = 0
        return score

    def span_score(span):
        score = 0
        for token in span: 
            score += word_score(token.text)
        return score

     # TODO this is key, how to score in corpus, but retain info on origin text?
    #generate span tuples, with origin text, start_char, end_char)
    scored_spans = {}
    for text in texts:
        doc = nlp(text.text)
        for span in [doc[i:i+sequence_length] for i in range(0, len(doc), sequence_length)]:
            html = add_annotations_to_span(span, text, project)
            score = span_score(span)
            scored_spans[html] = score

    return scored_spans # Dict with string key and score int value
    
def make_sorted_spans_for_seeds(request, no_seeds):
    project = get_object_or_404(Project, id=request.session.get("project_id"))
    texts = Text.objects.filter(projects=project)

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
    
    #Calculate word frequences within the entire corpus of project texts
    corpus = "".join([text.text for text in texts])
    corpus_doc = nlp(corpus)
    corpus_words = [token.text for token in corpus_doc]
    exceptions = ['\n']
    word_freq = Counter(word for word in corpus_words if word not in exceptions)
    seeds = word_freq.most_common(no_seeds)
    seed_spans = {}
    
    for word in seeds:
        seed_spans[word] = []
        for text in texts:
            matches = matcher(text.text, word[0], word[0]) # returns a list of tuples, start_char, end_char, label
        
            for match in matches:
                # check if annotation exists, else create, get id
                anotation, created = Annotation.objects.get_or_create(project=project, text=text, annotation_text=text.text[match[0]:match[1]], start_char=match[0], end_char=match[1], author_id=request.user.id)
                span = f'...' + text.text[match[0] - 50 :match[0]-1] + f'<a id="{anotation.id}" class="token" onclick="select_annotation(this)">'  + text.text[match[0]:match[1]] +'</a>' + text.text[match[1]+1:match[1]+50] + '...' #TODO use spaCy spans?
                seed_spans[word].append(span.replace('\n',''))
    return seed_spans
        
    # bulk-update controls 
    # click through spans in context press a = duplicate
       # A = duplicate all


def seeds(request, project, text):
    context = {}
    no_seeds = 10 #TODO add slider to adjust in UI
    if not request.session.get("seed_spans"):
        seed_spans = make_sorted_spans_for_seeds(request, no_seeds)
    else:
        seed_spans = request.session.get("seed_spans") 
    #context['sorted_spans'] = [span.text for span in sorted_scored_spans.keys()]
    print(seed_spans)
    context['seed_spans'] = seed_spans

    return render(request, "seeds.html", context)