from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.core.paginator import Paginator
from cadet_app.lang_utils import create_custom_spacy_language_object, clone_spacy_core, clone_custom_language



from cadet_app.utils import (
    make_dict,
    update_state,
    get_state,
    matcher,
    update_spacy_langs,
    add_annotations,
    export_tei,
    get_previous_and_next_text,
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


def set_text(request, id):
    text = Text.objects.get(pk=id)
    request.session["text_id"] = text.id
    request.session["text_title"] = text.title
    request.session["text_slug"] = text.text_slug
    return redirect(annotate, request.session.get("project_slug"), text.text_slug)

def set_labelset(request, id):
    labelset = LabelSet.objects.get(pk=id)
    project = get_object_or_404(Project, id=request.session.get("project_id"))
    project.label_set = labelset
    project.save()
    request.session["labelset_id"] = labelset.id
    request.session["labelset_title"] = labelset.title
    return redirect(data)

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

def language(request):
    #project_language = SpacyLanguage.objects.get(project__id=request.session.get("project_id"))
    languages = SpacyLanguage.objects.all()
    context = {}
    context['spacy_langs'] = languages
    project = get_object_or_404(Project, id=request.session.get("project_id"))
    if request.method == "POST":
        language = request.POST.get('language', None)
        language_data = request.POST.get('spacy_language', None)
        if not language:
            language = project.project_slug + '_' + spacy_language

        spacy_language, created = SpacyLanguage.objects.get_or_create(language=language)
        if created and not language_data: # Create new, no clone
            project.spacy_language = spacy_language
            project.language = language
            project.save()
            create_custom_spacy_language_object(language)

        if created and language_data: # Create new, clone from spacy/lang
            project.spacy_language = spacy_language
            project.language = language
            project.save()
            clone, created= SpacyLanguage.objects.get_or_create(id=language_data)
            if clone.is_core:
                clone_spacy_core(language, clone)
            else:
                clone_custom_language(language, clone)


        else:
            # Language already exists 
            project.spacy_language = spacy_language
            project.save()

        
        messages.info(request, "Project language updated successfully")
        request.session["project_language"] = language
        return render(request, "language.html", context)    

    context['form'] = ProjectLanguageForm(instance=project)
    return render(request, "language.html", context)

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
            language = get_object_or_404(Project, id=request.session.get("project_id")).language
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
    context = {}
    context["anno_types"] = AnnotationType.objects.all()
    context["labelsets"] = LabelSet.objects.all().order_by('-id')

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

    context["annotation_types"] = AnnotationType.objects.all()
    context["table_columns"] = Project.objects.get(id=project).label_set.groups.all()
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
