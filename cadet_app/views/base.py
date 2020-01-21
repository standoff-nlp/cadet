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

@login_required(redirect_field_name="", login_url="login/")
def index(request):

    if request.method == "POST":
        update_state(request)
        return render(request, "index.html",)

    else:
        return render(request, "index.html",)


def site_login(request):
    if request.method == "POST":
        user = authenticate(
            username=request.POST["username"], password=request.POST["password"]
        )
        print(user or "user not found")
        if user is not None:
            login(request, user)
            return redirect(index)
        else:
            return render(
                request, "login.html", {"message": "Incorrect, please try again"}
            )

    else:
        return render(request, "login.html")


@psa("social:complete")
def register_by_access_token(request, backend):
    # This view expects an access_token GET parameter, if it's needed,
    # request.backend and request.strategy will be loaded with the current
    # backend and strategy.
    token = request.GET.get("access_token")
    user = request.backend.do_auth(token)
    if user:
        login(request, user)
        return redirect(index)
    else:
        return render(request, "login.html")


def site_logout(request):
    logout(request)
    return redirect(site_login)

def set_text(request, id):
    text = Text.objects.get(pk=id)
    request.session["text_id"] = text.id
    request.session["text_title"] = text.title
    request.session["text_slug"] = text.text_slug
    return redirect(annotate, request.session.get("project_slug"), text.text_slug)

