from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


from cadet_app.utils import make_dict, update_state, get_state, matcher, update_spacy_langs
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
    return redirect(projects)

def data(request):
    texts = Text.objects.all()
    if request.method == "POST":

        form = TextForm(request.POST, request.FILES)
        if form.is_valid():
            text = form.save()
            text.author = request.user
            text.projects.add(request.session.get('project_id'))
            text.save()


            context = {}
            context["form"] = form
            context["texts"] = texts
            title = request.POST['title']
            language = request.POST['language']
            context["message"] = handle_uploaded_file(request, language, text, title)

            return render(request, "data.html", context)

    else:
        form = TextForm()
        context = {}
        context["form"] = form
        context["texts"] = texts

        return render(request, "data.html", context)

def labels(request):
    return render(request, "labels.html",)


def annotate(
    request, text, token
):  # Version of the annotation UI from scratch
    try:
        project = request.session.get('project_id')

    except AttributeError:
        messages.info(request, "Please select a project before proceeding")
        #messages.add_message(request, messages.INFO, "Please select a project before proceeding")
        return redirect(projects)

    context = {}
    try:
        context["project"] = Project.objects.get(id=request.session.get('project_id'))
    except Exception as e:
        messages.info(request, "Please select a project before proceeding")
        #messages.add_message(request, messages.INFO, "Please select a project before proceeding")
        return redirect(projects)

    # TODO function to query project texts, return text for annotation 
    # send text
    # send tokens
    # send spans 
    # send sentences 

    #text = Text.objects.get(pk=text)
    #sentence = Sentence.objects.get(text=text, pk=sentence)
    #token = Token.objects.get(pk=token, project=project, text=text)

    
    #context["project"] = project
    #context["text"] = text
    #context["sentence"] = sentence
    #context["token"] = token

    # sort texts term freqency/ strategic annotation
    return render(request, "annotate.html", context)

def annotate0(
    request, project, text, sentence, token
):  # Version of the annotation UI from scratch
    project = Project.objects.get(pk=project)
    #text = Text.objects.get(pk=text)
    #sentence = Sentence.objects.get(text=text, pk=sentence)
    #token = Token.objects.get(pk=token, project=project, text=text)

    context = {}
    #context["project"] = project
    #context["text"] = text
    #context["sentence"] = sentence
    #context["token"] = token

    # sort texts term freqency/ strategic annotation
    return render(request, "annotate0.html", context)


def annotate1(request):  # Version of the annotation UI using annotator.js

    # sort texts term freqency/ strategic annotation
    return render(request, "annotate1.html",)


def export(request):
    return render(request, "export.html",)
