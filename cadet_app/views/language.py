from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.http import JsonResponse
import re
from cadet_app.lang_utils import create_spacy_language, clone_spacy_language, create_stop_words, create_examples
from pathlib import Path
from django.conf import settings
from spacy.cli.download import *

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
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape, format_html, mark_safe
import spacy

def language(request):
    # TODO get list of spaCy core models from Path(settings.CUSTOM_LANGUAGES_DIRECTORY) / 'core_models'
    # create select field to choose core model to import for inital defauls on pipelines
    # figure out how to assert compatibility of model versions with current spaCy version, compatibility.json

    #project_language = SpacyLanguage.objects.get(project__id=request.session.get("project_id"))
    languages = SpacyLanguage.objects.all()
    context = {}
    context['spacy_langs'] = languages
    project = get_object_or_404(Project, id=request.session.get("project_id"))
    context['form'] = ProjectLanguageForm(instance=project)
    if request.method == "POST":
        language = request.POST.get('language', None)
        language_data = request.POST.get('spacy_language', None)
        core_model = request.POST.get('core_model', None)

        print(language, language_data, core_model)

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

            if created and language_data and core_model != "None":
                project.spacy_language = spacy_language
                project.language = language
                project.core_model = core_model
                project.save()
                clone, created= SpacyLanguage.objects.get_or_create(id=language_data)
                clone_spacy_language(language, clone, core_model)

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

def exact_match(word:str, text:str) -> tuple:
    """This helper function is used to find an exact match, and only an exact match in
    a set"""
    import re
    regex = rf"\b{word}\b"
    matches = re.finditer(regex, text, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        #TODO assert only one match
        return match.start(), match.end()

#TODO add_stop_words
def add_stop_words(request):
    if request.method == "GET":
        project = get_object_or_404(Project, id=request.session.get("project_id"))
        language = project.spacy_language.slug.replace('-','_')
        new = request.GET.get('new', None)
        if new:
            path = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/lang/' + language) / 'stop_words.py'
            script = path.read_text()
            start = script.find('"""') + 4
            if start:
                new_script = script[:start] + ' ' +new + ' ' + script[start:]
                path.write_text(new_script)
                messages.success(request, "Stop word added successfully")
        # Next update the stop words, coming from the db or file?
        return redirect(stop_words)

def delete_stop_words(request, word):
    project = get_object_or_404(Project, id=request.session.get("project_id"))
    language = project.spacy_language.slug.replace('-','_')
    path = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/lang/' + language) / 'stop_words.py'
    script = path.read_text()
    start, end = exact_match(word,script)
    new_script = script[:start] + script[end:]
    path.write_text(new_script)
    messages.success(request, "Stop word deleted successfully")
    return redirect(stop_words)

def update_stop_words(request):
    if request.method == "GET":
        project = get_object_or_404(Project, id=request.session.get("project_id"))
        language = project.spacy_language.slug.replace('-','_')
        old = request.GET.get('old', None)
        new = request.GET.get('new', None)
        if new:
            path = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/lang/' + language) / 'stop_words.py'
            script = path.read_text()
            start, end = exact_match(old,script)
            new_script = script[:start] + new + script[end:]
            path.write_text(new_script)
            messages.success(request, "Stop word updated successfully")
        # Next update the stop words, coming from the db or file?
        return redirect(stop_words)

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

def lemma_json(request):
    project = get_object_or_404(Project, id=request.session.get("project_id"))
    language = project.spacy_language.slug.replace('-','_')
    try:
        path = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/lookups-data/')
        filename = language + '_lemma_lookup.json.gz'
        path = path / filename
        print(str(path))
        assert path.exists()
        with gzip.open(str(path), 'rb') as f:
            data= {}
            data['data'] = []
            lemmata = dict(json.load(f))
            for lemma in lemmata:
                data['data'].append({"Word":f"{lemma}", "Lemma": f"{lemmata[lemma]}"})

            return JsonResponse(
               data,
            )
    except AssertionError:
        print('fish eat other fish')# TODO add create lemmata json file

class LemmaJson(BaseDatatableView):
    # the model you're going to show
    model = Lemma


    columns = ['word','lemma']
    order_columms = ['word','lemma']
    # set max limit of records returned
    # this is used to protect your site if someone tries to attack your site and make it return huge amount of data
    max_display_length = 500

    def get_initial_queryset(self):
        project = get_object_or_404(Project, id=self.request.session.get("project_id"))
        try:
            language = project.spacy_language.slug.replace('-','_')
        except AttributeError: # Until language is created, language is none
            language = 'english'

        # Check if lemmata for this project and language exist, if not create them from the json
        lemmata = Lemma.objects.filter(project=project)
        if not lemmata:
            path = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/lookups-data/')
            filename = language + '_lemma_lookup.json.gz'
            path = path / filename
            if path.exists():
                with gzip.open(str(path), 'rb') as f:
                    data = json.load(f)
                    for word in data:
                        Lemma.objects.update_or_create(
                            spacy_language=project.spacy_language,
                            project=project,
                            word=word,
                            lemma=data[word],
                            auto_generated=True,
                            )

            else:
                filename = language + '_lemma_lookup.json'
                path = path / filename
                if path.exists():
                    messages.info(self.request, '[*] need to add handling for uncompressed json lemmata!')


        return self.model.objects.filter(spacy_language=project.spacy_language, project=project)


    def render_column(self, row, column):

        #print(row, column)
        #for label in row.labels.all():
        #    if label == "FORM":
        #        return format_html(row.annotation_text)

            #return format_html(row)

        return super(LemmaJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # here is a simple example
        search = self.request.GET.get('search[value]', None)
        if search:
            q = Q(word__icontains=search) | Q(lemma_icontains=search)
            qs = qs.filter(q)
        return qs
