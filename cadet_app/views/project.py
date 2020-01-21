# TODO Help views is out of control!  Try something like this: https://simpleisbetterthancomplex.com/tutorial/2016/08/02/how-to-split-views-into-multiple-files.html
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

from .language import language

@login_required(login_url="login")
def projects(request):
    # TODO limit visible projects based on user permissions

    projects = Project.objects.all()
    context = {}
    context["projects"] = projects
    return render(request, "projects.html", context)

# TODO are both add and edit project needed?
@login_required(redirect_field_name="", login_url="login/")
def add_project(request):

    if request.method == "POST":
        form = ProjectForm(request.POST)
        form.save()
        project = form.instance
        request.session["project_id"] = project.id
        request.session["project_title"] = project.title
        request.session["project_slug"] = project.project_slug
        request.session["project_language"] = project.language
        request.session["text_id"] = None
        request.session["text_title"] = None
        request.session["text_slug"] = None
        request.session["labelset_title"] = None


        return redirect(language)

    else:
        form = ProjectForm()
        context = {}
        context["form"] = form

        return render(request, "add_project.html", context)


@login_required(redirect_field_name="", login_url="login/")
def edit_project(request, id):
    print(request.POST.__dict__)
    if request.method == "POST":
        project = get_object_or_404(Project, pk=id)
        form = ProjectForm(request.POST or None, instance=project)
        if form.is_valid():
            form.save()
            return redirect(projects)

    else:
        project = get_object_or_404(Project, pk=id)
        form = ProjectForm(request.POST or None, instance=project)
        context = {}
        context["form"] = form

        return render(request, "add_project.html", context)


def set_project(request, id):
    project = Project.objects.get(pk=id)
    if project.language:
        request.session["project_language"] = project.language
    if project.label_set:
        request.session["labelset_title"] = project.label_set.title
    request.session["project_id"] = project.id
    request.session["project_title"] = project.title
    request.session["project_slug"] = project.project_slug
    if request.user.is_staff:
        return redirect(language)
    else:
        return redirect(data)
