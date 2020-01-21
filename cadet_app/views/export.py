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

def export(request):

    project = Project.objects.get(id=request.session.get("project_id"))
    text = Text.objects.get(id=request.session.get("text_id"))

    if request.method == "POST":

        export_type = request.POST.get("export_type", None)

        if export_type == "TEI":
            content = export_tei(
                text, project
            )  # TODO new function that returns TEI not HTML
            filename = slugify(f"{ project.title}{text.title}") + ".xml"
            response = HttpResponse(content, content_type="xml/tei")
            response["Content-Disposition"] = "attachment; filename={0}".format(
                filename
            )
            return response

    else:
        return render(request, "export.html",)
