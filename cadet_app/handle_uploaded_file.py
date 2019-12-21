from cadet_app.models import *
from iso639 import languages
import spacy
from cadet_app.utils import (
    add_annotations,
)


def handle_text_file(request, nlp, current_text):
    file = request.FILES["file"]
    text = str(file.read().decode("utf-8"))
    current_text.text = text  #
    current_text.save()
    if nlp:  # spaCy language object present
        

        doc = nlp(text)

        if nlp.has_pipe("sentencizer"):
            for sent in doc.sents:
                new_sent = Annotation(
                    author=request.user,
                    project=Project.objects.get(id=request.session.get("project_id")),
                    annotation_type=AnnotationType.objects.get(name="sent"),
                    annotation_text=sent.text,
                    text=current_text,
                )
                new_sent.save()

            for token in doc:
                start_char = token.idx

                new = Annotation(
                    author=request.user,
                    project=Project.objects.get(id=request.session.get("project_id")),
                    annotation_type=AnnotationType.objects.get(name="token"),
                    annotation_text=token.text,
                    text=current_text,
                    start_char=start_char,
                )
                new.save()

        else:
            for token in doc:
                start_char = token.idx

                new = Annotation(
                    author=request.user,
                    project=Project.objects.get(id=request.session.get("project_id")),
                    annotation_type=AnnotationType.objects.get(name="token"),
                    annotation_text=token.text,
                    text=current_text,
                    start_char=start_char,
                )
                new.save()
    current_text.standoff = add_annotations(current_text, Project.objects.get(id=request.session.get("project_id")))
    current_text.save()
    

def handle_uploaded_file(request, language, text, title):
    file = request.FILES["file"]
    
    try:
        if text.spacy_language.iso:
            lang = spacy.util.get_lang_class(text.spacy_language.iso)
            nlp = lang()

        if file.content_type == "text/plain":
            handle_text_file(request, nlp, text)

        if file.content_type == "text/csv":
            # doc = nlp(file.read())
            return "Dataset added successfully. Select datasets below or add another."

        if file.content_type == "xml/tei":
            # TODO use standoff converter to create text/sentence/tokens (same as above) and annotations.
            pass

        if file.content_type == "application/octet-stream":  # CoNNL-U
            pass
        return "Have a nice day!"

    except Exception as e: 
        print(e)
        nlp = None
        if file.content_type == "text/plain":
            handle_text_file(request, nlp, text)


def handle_url_file(request, language, text, title):
    pass
