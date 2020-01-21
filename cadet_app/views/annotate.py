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
from .project import projects

def annotate(request, project, text):
    try:
        project = request.session.get("project_id")

    except AttributeError:
        messages.info(request, "Please select a project before proceeding")
        return redirect(projects)

    context = {}
    try:
        context["project"] = Project.objects.get(id=request.session.get("project_id"))
    except Exception as e:
        messages.info(request, "Please select a project before proceeding")
        return redirect(projects)

    context["annotation_types"] = AnnotationType.objects.all()
    context["table_columns"] = Project.objects.get(id=project).label_set.groups.all() # TODO order by sequence in label set
    context["previous_text"], context["next_text"] = get_previous_and_next_text(project, text)
    # Need default text window size 2 sents=50, user can zoom in and out within range 100
    # 100 = len(text),
    # split the text into parts, forward and back links for parts
    # need to mark existing annotation in the text html
    text = Text.objects.get(text_slug=text)
    context["annotations"] = Annotation.objects.filter(
        project=Project.objects.get(id=project), text=text
    ).order_by("start_char")

    # context["annotations"] = Annotation.objects.filter(project=project, text=text) # TODO delete this if not needed
    window = None

    # adjust text to fit within viewframe
    context["text"] = text

    if text.strategic_anno is True:
        messages.info(request, "Strategic annotations is set to True")

    if text.strategic_anno is False or None:
        messages.info(request, "Strategic annotations is set to False")

    # Django paginator, so split the text into segments https://docs.djangoproject.com/en/3.0/topics/pagination/
    # TODO
    
    context["text_html"] = text.standoff


    if request.method == "POST":
        # context["text_html"] = add_annotations(text, project)
        
        modal_form = AnnotationForm(request.POST, project=project)

        if modal_form.is_valid():
            context["modal_form"] = modal_form
            modal_form = modal_form.save(commit=False)
            modal_form.start_char = request.POST.get("sel-start-value", None)
            modal_form.end_char = request.POST.get("sel-end-value", None)

            modal_form.annotation_text = request.POST.get("sel-text-value", None)
            modal_form.author = request.user
            modal_form.auto_generated = False
            modal_form.text = Text.objects.get(id=request.session.get("text_id"))
            modal_form.project = Project.objects.get(
                id=request.session.get("project_id")
            )
            modal_form.save()

            messages.success(request, "Annotation added successfully")
            return render(request, "annotate.html", context)

    else:
        modal_form = AnnotationForm(project=project)
        context["modal_form"] = modal_form
        return render(request, "annotate.html", context)

def add_annotation_form(request, id):
    pass

def edit_annotation(request, id):
    if request.method == "POST":
        project = Project.objects.get(id=request.session.get("project_id"))
        form = EditAnnotationForm(request.POST, request.FILES, project=project.id, user=request.user)
        if form.is_valid():
            form.save()
            instance = get_object_or_404(Annotation, id=id)
            project = Project.objects.get(id=request.session.get("project_id"))
            context = {}
            context["edit_annotation_form"] = EditAnnotationForm(
                project=project.id, instance=instance
            )

            return render(request, "edit_annotation_form.html", context)
    else:

        """A view that renders a modelform for an existing annotation.  The form's html is retrieved by ajax.  jquery updates the edit_annotation div"""
        instance = get_object_or_404(Annotation, id=id)
        project = Project.objects.get(id=request.session.get("project_id"))
        context = {}
        context["edit_annotation_form"] = EditAnnotationForm(
            project=project.id, instance=instance, user=request.user,
        )

        return render(request, "edit_annotation_form.html", context)

def edit_annotation_no_id(request):
    pass