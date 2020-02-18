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

def set_text(request, id):
    text = Text.objects.get(pk=id)
    request.session["text_id"] = text.id
    request.session["text_title"] = text.title
    request.session["text_slug"] = text.text_slug
    return redirect(data)
    #return redirect(a, request.session.get("project_slug"), text.text_slug)

def delete_text(request, id):
    text = Text.objects.get(pk=id)
    text.delete()
    return redirect(data)

@login_required(redirect_field_name="", login_url="login/")
def edit_text(request, id):

    if request.method == "POST":
        text = get_object_or_404(Text, pk=id)
        form = TextForm(request.POST or None, instance=text)
        if form.is_valid():
            form.save()
            return redirect(data)

    else:
        text = get_object_or_404(Text, pk=id)
        form = TextForm(request.POST or None, instance=text)
        context = {}
        context["form"] = form

        return render(request, "add_project.html", context)

def data(request):
    all_texts = Text.objects.all()
    project_texts = Text.objects.filter(projects__id=request.session.get("project_id"))
    if request.method == "POST":

        form = TextForm(request.POST, request.FILES)
        if form.is_valid():
            text = form.save()
            text.author = request.user
            text.projects.add(request.session.get("project_id"))
            text.save()

            context = {}
            context["form"] = form
            context["all_texts"] = all_texts
            context["project_texts"] = project_texts
            title = request.POST["title"]
            project_language = get_object_or_404(Project, id=request.session.get("project_id")).spacy_language
            if request.FILES["file"]:
                context["message"] = handle_uploaded_file(
                    request, project_language, text, title
                )
            if request.session.get("url", None):
                context["message"] = handle_url_file(request, project_language, text, title)

            if request.user.is_staff:
                return render(request, "data.html", context)
            else:
                return render(request, "data_public.html", context)

    else:
        form = TextForm()
        context = {}
        context["form"] = form
        context["all_texts"] = all_texts
        context["project_texts"] = project_texts

        if request.user.is_staff:
            return render(request, "data.html", context)
        else:
            return render(request, "data_public.html", context)
