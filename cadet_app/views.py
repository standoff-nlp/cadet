from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required


from cadet_app.utils import (
    make_dict,
    update_state,
    get_state,
    matcher,
    update_spacy_langs,
    add_annotations,
)
from cadet_app.handle_uploaded_file import handle_uploaded_file, handle_url_file
from cadet_app.models import *
from cadet_app.forms import ProjectForm, TextForm, AnnotationForm, AnnotationTypeForm
from social_django.utils import psa

import spacy

# update_spacy_langs()

# Create your views here.
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


@login_required(login_url="login")
def projects(request):
    # TODO limit visible projects based on user permissions

    projects = Project.objects.all()
    context = {}
    context["projects"] = projects
    return render(request, "projects.html", context)


@login_required(redirect_field_name="", login_url="login/")
def add_project(request):

    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(projects)

    else:
        form = ProjectForm()
        context = {}
        context["form"] = form

        return render(request, "add_project.html", context)


@login_required(redirect_field_name="", login_url="login/")
def edit_project(request, id):

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
    request.session["project_id"] = project.id
    request.session["project_title"] = project.title
    request.session["project_slug"] = project.project_slug
    return redirect(data)


def set_text(request, id):
    text = Text.objects.get(pk=id)
    request.session["text_id"] = text.id
    request.session["text_title"] = text.title
    request.session["text_slug"] = text.text_slug
    return redirect(annotate, request.session.get("project_slug"), text.text_slug)


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


def data(request):

    # TODO auto-select texts already associated with current project

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
            language = request.POST["language"]
            if request.FILES["file"]:
                context["message"] = handle_uploaded_file(
                    request, language, text, title
                )
            if request.session.get("url", None):
                context["message"] = handle_url_file(request, language, text, title)

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


def labels(request):

    anno_types = AnnotationType.objects.all()
    context = {}
    context["anno_types"] = anno_types

    return render(request, "labels.html", context)


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

    # Need default text window size 2 sents=50, user can zoom in and out within range 100
    # 100 = len(text),
    # split the text into parts, forward and back links for parts
    # need to mark existing annotation in the text html
    text = Text.objects.get(text_slug=text)
    print(request.__dict__)
    annotations = Annotation.objects.filter(text=text)
    window = None
    text_ooo = add_annotations(text, project)
    # adjust text to fit within viewframe
    context["text"] = text

    if text.strategic_anno is True:
        messages.info(request, "Strategic annotations is set to True")

    if text.strategic_anno is False or None:
        messages.info(request, "Strategic annotations is set to False")

    if request.method == "POST":

        modal_form = AnnotationForm(request.POST)
        context["modal_form"] = modal_form
        if modal_form.is_valid():
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
        modal_form = AnnotationForm()
        context["modal_form"] = modal_form
        return render(request, "annotate.html", context)


def export(request):
    return render(request, "export.html",)
