from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.core.paginator import Paginator
from cadet_app.lang_utils import create_spacy_language, clone_spacy_language, create_stop_words, create_examples
from pathlib import Path
from django.conf import settings
import sys
import json
import gzip

from cadet_app.utils import (
    make_dict,
    update_state,
    get_state,
    get_sentences,
    matcher,
    update_spacy_langs,
    add_annotations,
    export_tei,
    get_previous_and_next_text,
    put_spans_around_tokens,
    blank_examples,
)
from cadet_app.handle_uploaded_file import handle_uploaded_file, handle_url_file
from cadet_app.models import *
from cadet_app.forms import (
    ProjectForm,
    ProjectLanguageForm,
    TextForm,
    AnnotationForm,
    EditAnnotationForm,
    AnnotationTypeForm,
    TokenTestForm,
    AddExampleSentenceForm,
)
from social_django.utils import psa

import spacy

def language(request):
    #project_language = SpacyLanguage.objects.get(project__id=request.session.get("project_id"))
    languages = SpacyLanguage.objects.all()
    context = {}
    context['spacy_langs'] = languages
    project = get_object_or_404(Project, id=request.session.get("project_id"))
    context['form'] = ProjectLanguageForm(instance=project)
    if request.method == "POST":
        language = request.POST.get('language', None)
        language_data = request.POST.get('spacy_language', None)
        
        # neither field has an entry
        if language == '' and not language_data:
            language = slugify(project.title).replace('-','_')

        # language, but no language data 
        if language == '' and language_data:
            language = SpacyLanguage.objects.get(id=language_data).language

        else:
            spacy_language, created = SpacyLanguage.objects.get_or_create(language=language)
            if created and not language_data: # Create new, no clone
                project.spacy_language = spacy_language
                project.language = language
                project.save()
                create_spacy_language(language)

            if created and language_data: # Create new, clone from spacy/lang or custom_languages
                project.spacy_language = spacy_language
                project.language = language
                project.save()
                clone, created= SpacyLanguage.objects.get_or_create(id=language_data)
                clone_spacy_language(language, clone)

            else:
                # Language already exists 
                project.spacy_language = spacy_language
                project.save()

        
        messages.info(request, "Project language updated successfully")
        request.session["project_language"] = language
        return render(request, "language.html", context)    

    return render(request, "language.html", context)

def stop_words(request):
    context = {}

    #open 
    project = get_object_or_404(Project, id=request.session.get("project_id"))
    language = project.spacy_language.slug.replace('-','_')
    try:
        path = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/lang/' + language) / 'stop_words.py'
        assert path.exists()
    except AssertionError:
        path = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/lang/' + language)
        create_stop_words(path) 

    import importlib.util # TODO clean this up  https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
    spec = importlib.util.spec_from_file_location("STOP_WORDS", str(path))
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)
    words = foo.STOP_WORDS
    context['stop_words'] = words
    return render(request, "language.html", context)

def examples(request):
    context = {}
    if request.method == "POST":
        new_sentence = request.POST.get('sentences', None)
        messages.success(request, "Example sentences have been updated")
    sentences = get_sentences(request)
    context['add_example_form'] = AddExampleSentenceForm(initial={'sentences': sentences})

    return render(request, "language.html", context)

def lemmata(request):
    context = {}

    #open 
    project = get_object_or_404(Project, id=request.session.get("project_id"))
    language = project.spacy_language.slug.replace('-','_')
    try:
        path = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/lookups-data/') 
        filename = language + '_lemma_lookup.json.gz'
        path = path / filename
        print(str(path))
        assert path.exists()
        with gzip.open(str(path), 'rb') as f: 
            context['lemmata'] = json.load(f)
    except AssertionError:
        print('fish eat other fish')# TODO add create lemmata json file 

    context['sentences'] = get_sentences(request)
    return render(request, "language.html", context)

def tokenization(request):
    context = {}

    #open 
    project = get_object_or_404(Project, id=request.session.get("project_id"))
    language = project.spacy_language.slug.replace('-','_')
    exceptions = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/lang/' + language) / 'tokenizer_exceptions.py'
    lang = spacy.util.get_lang_class(language)
    nlp = lang()

    if request.method == "POST":
        tokenize_this = request.POST.get('text', None)
        doc = nlp(tokenize_this)
        doc = put_spans_around_tokens(doc)
        context['doc'] = doc
    else:
        sentences = get_sentences(request)
        sentences = ''.join([sent + '\n' for sent in sentences]) 
        form = TokenTestForm(initial={'text': sentences})
        context['tokenization_form'] = form
    return render(request, "language.html", context)