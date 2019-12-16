from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


from cadet_app.utils import make_dict, update_state, get_state, matcher, update_spacy_langs, prepare_text
from cadet_app.handle_uploaded_file import handle_uploaded_file
from cadet_app.models import *
from cadet_app.forms import ProjectForm, TextForm
from social_django.utils import psa

import spacy
#update_spacy_langs()
    
# Create your views here.
@login_required(redirect_field_name='', login_url='login/')
def index(request):
    
    if request.method == "POST":
        update_state(request)
        return render(request, "index.html",)


    else:
        return render(request, "index.html",)

def site_login(request):
    if request.method == "POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        print(user or "user not found")
        if user is not None:
            login(request, user)
            return redirect(index)
        else:
            return render(request, "login.html", {'message': 'Incorrect, please try again'})

    else:
        return render(request, "login.html")

@psa('social:complete')
def register_by_access_token(request, backend):
    # This view expects an access_token GET parameter, if it's needed,
    # request.backend and request.strategy will be loaded with the current
    # backend and strategy.
    token = request.GET.get('access_token')
    user = request.backend.do_auth(token)
    if user:
        login(request, user)
        return redirect(index)
    else:
        return render(request, "login.html")

def site_logout(request):
    logout(request)
    return redirect(site_login)


@login_required(login_url='login')
def projects(request):

    projects = Project.objects.all()
    context = {}
    context['projects'] = projects
    return render(request, "projects.html", context)

@login_required(redirect_field_name='', login_url='login/')
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

@login_required(redirect_field_name='', login_url='login/')
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
    request.session['project_id'] = project.id
    request.session['project_title'] = project.title
    request.session['project_slug'] = project.project_slug
    return redirect(projects)

def set_text(request, id):
    text = Text.objects.get(pk=id)
    request.session['text_id'] = text.id
    request.session['text_title'] = text.title
    request.session['text_slug'] = text.text_slug
    return redirect(annotate, request.session.get('project_slug'), text.text_slug)

def delete_text(request, id):
    text = Text.objects.get(pk=id)
    text.delete()
    return redirect(data)

@login_required(redirect_field_name='', login_url='login/')
def edit_text(request, id):
    
    if request.method == "POST":
        project = get_object_or_404(Project, pk=id)
        form = TextForm(request.POST or None, instance=project)
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

    # TODO auto-select texts already associated with current project

    all_texts = Text.objects.all()
    project_texts = Text.objects.filter(projects__id=request.session.get('project_id'))
    if request.method == "POST":

        form = TextForm(request.POST, request.FILES)
        if form.is_valid():
            text = form.save()
            text.author = request.user
            text.projects.add(request.session.get('project_id'))
            text.save()


            context = {}
            context["form"] = form
            context["all_texts"] = all_texts
            context["project_texts"] = project_texts
            title = request.POST['title']
            language = request.POST['language']
            context["message"] = handle_uploaded_file(request, language, text, title)

            return render(request, "data.html", context)

    else:
        form = TextForm()
        context = {}
        context["form"] = form
        context["all_texts"] = all_texts
        context["project_texts"] = project_texts

        return render(request, "data.html", context)

def labels(request):
    return render(request, "labels.html",)


def annotate(
    request, project, text
):  
    try:
        project = request.session.get('project_id')

    except AttributeError:
        messages.info(request, "Please select a project before proceeding")
        return redirect(projects)

    context = {}
    try:
        context["project"] = Project.objects.get(id=request.session.get('project_id'))
    except Exception as e:
        messages.info(request, "Please select a project before proceeding")
        return redirect(projects)
    
    # Need default text window size 2 sents=50, user can zoom in and out within range 100
    #100 = len(text), 
    # split the text into parts, forward and back links for parts 
    # need to mark existing annotation in the text html
    text = Text.objects.get(text_slug=text)
    print(request.__dict__)
    annotations = Annotation.objects.filter(text=text)
    window = None
    text_ooo = prepare_text(text, window)
    # adjust text to fit within viewframe 
    context["text"] = text

    if text.strategic_anno is True:
        messages.info(request, "Strategic annotations is set to True")

    if text.strategic_anno is False or None:
        messages.info(request, "Strategic annotations is set to False")
    
    return render(request, "annotate.html", context)

def export(request):
    return render(request, "export.html",)
