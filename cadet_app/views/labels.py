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
from .text import data
from .project import projects


def labels(request):
    context = {}
    context["anno_types"] = AnnotationType.objects.all()
    context["labelsets"] = LabelSet.objects.all().order_by('-id')

    return render(request, "labels.html", context)

def set_labelset(request, id):
    labelset = LabelSet.objects.get(pk=id)
    project = get_object_or_404(Project, id=request.session.get("project_id"))
    project.label_set = labelset
    project.save()
    request.session["labelset_id"] = labelset.id
    request.session["labelset_title"] = labelset.title
    return redirect(data)

@staff_member_required
def edit_annotation_type(request, id):

    if request.method == "POST":
        anno_type = get_object_or_404(AnnotationType, pk=id)
        form = AnnotationTypeForm(request.POST or None, instance=anno_type)
        if form.is_valid():
            form.save()
            return redirect(labels)

    else:
        anno_type = get_object_or_404(AnnotationType, pk=id)
        form = AnnotationTypeForm(request.POST or None, instance=anno_type)
        context = {}
        context["form"] = form

        return render(request, "add_project.html", context)


@login_required(redirect_field_name="", login_url="login/")
def add_annotation_type(request):

    if request.method == "POST":
        form = AnnotationTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(projects)

    else:
        form = AnnotationTypeForm()
        context = {}
        context["form"] = form

        return render(request, "add_project.html", context)