from cadet_app.models import *
from iso639 import languages
import spacy
from cadet_app.utils import add_annotations
from django.conf import settings
from pathlib import Path

def handle_text_file(request, nlp, current_text):
    file = request.FILES["file"]
    text = str(file.read().decode("utf-8"))
    current_text.text = text  #
    current_text.save()

    project = Project.objects.get(id=request.session.get("project_id"))
    if nlp:  # spaCy language object present

        doc = nlp(text)

        # mark all model suggestions as auto_generated = True
        if nlp.has_pipe("parser"): # https://spacy.io/usage/processing-pipelines
            for sent in doc.sents:
                new_sent = Annotation(
                    author=request.user,
                    project=project,
                    annotation_type=AnnotationType.objects.get(name="sent"),
                    annotation_text=sent.text,
                    start_char=sent.start_char,
                    end_char=sent.start_char + len(sent.text)
                    text=current_text,
                )
                new_sent.save()

        if nlp.has_pipe("ner"): # named entitites
            for ent in doc.ents:
                pass # TODO add this 

        if nlp.has_pipe("tagger"): # POS
            for token in doc:
                start_char = token.idx
                end_char = start_char + len(token.text)
                pos = token.pos_
                label, created = Label.object.get_or_create(name=pos)
                Annotation.objects.update_or_create(
                    project=project,
                    annotation_type=AnnotationType.objects.get(name="token"),
                    annotation_text=token.text,
                    text=current_text,
                    start_char=start_char,
                    end_char=end_char
                )
            
        for token in doc:
            start_char = token.idx

            new = Annotation(
                author=request.user,
                project=project,
                annotation_type=AnnotationType.objects.get(name="token"),
                annotation_text=token.text,
                text=current_text,
                start_char=start_char,
            )
            new.save()

    # TODO this needs to be changed, will generate standoff dynamically
    current_text.standoff = add_annotations(
        current_text, project
    )
    current_text.save()


def handle_uploaded_file(request, project_language, text, title):
    file = request.FILES["file"]
    # TODO check if model directory exists for the language, if so, load the model
    model_path = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/models/' + project_language)
    if model_path.exists():
        nlp = spacy.load(str(model_path))
        
    else:
        lang = spacy.util.get_lang_class(project_language.slug.replace('-','_'))
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

        


def handle_url_file(request, language, text, title):
    pass
