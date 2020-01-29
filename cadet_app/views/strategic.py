from django.shortcuts import render, get_object_or_404, redirect
from collections import Counter


def generate_sequences(sequence_length):
    """This is a utility function used to generate a sorted list of sequences for annotation.
    To preserve resources, the function is run once and then saved to session, rather than
    every time the page is loaded"""
    project = get_object_or_404(Project, id=request.session.get("project_id"))
    texts = Text.objects.filter(projects=project)
    texts = "".join([text.text for text in texts])

    # split the text into equal chunks for sorting https://stackoverflow.com/questions/13673060/split-string-into-strings-by-length
    sequences = [texts[i:i+chunk_size] for i in range(0, len(texts), sequence_length)]

    project_language = project.spacy_language.slug.replace('-','_')
    model_path = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/models/' + project_language )
    if model_path.exists():
        nlp = spacy.load(str(model_path))
        
    else:
        lang = spacy.util.get_lang_class(project_language)
        nlp = lang()
    
    doc = nlp(text)
    # https://stackoverflow.com/questions/37253326/how-to-find-the-most-common-words-using-spacy
    words = [token.text for token in doc if token.is_stop != True and token.is_punct != True]
    word_freq = dict(Counter(words))

    #count common terms, unique terms, 
    def word_score(word:str):
        if word in word_freq.keys():
            score = word_freq[word]
        else:
            score = 0
        return score

def strategic(request, project, text):
    

    # split text into segments
    # score segments, sum of words
    #Find n-long segments with highest frequency of frequent terms

    context = {}
    return render(request, "strategic.html", context)