from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login

from cadet_app.utils import make_dict, update_state, get_state, matcher, handle_uploaded_file
from cadet_app.models import *
from cadet_app.forms import ProjectForm, DatasetForm
import spacy

    
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
        print(user or "fish")
        if user is not None:
            login(request, user)
            return redirect(index)
        else:
            return render(request, "login.html", {'message': 'Incorrect, please try again'})

    else:
        return render(request, "login.html")

def home(request):
    if request.method == "POST":
        update_state(request)
        return redirect("table/diaries")

    else:
        return render(request, "index.html",)


def projects(request):

    projects = Project.objects.all()
    context = {}
    context['projects'] = projects
    return render(request, "projects.html", context)


def add_project(request):

    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()

            return render(request, "projects.html")

    else:
        form = ProjectForm()
        context = {}
        context["form"] = form

        return render(request, "add_project.html", context)

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
    projects = Project.objects.all()
    context = {}
    context['projects'] = projects
    return render(request, "projects.html", context)

def data(request):
    datasets = Dataset.objects.all()
    if request.method == "POST":

        form = DatasetForm(request.POST, request.FILES)
        if form.is_valid():
            dataset = form.save()
            context = {}
            context["form"] = form
            context["datasets"] = datasets
            title = request.POST['title']
            language = request.POST['language']
            context["message"] = handle_uploaded_file(request.FILES['file'], language, dataset)

            return render(request, "data.html", context)

    else:
        form = DatasetForm()
        context = {}
        context["form"] = form
        context["datasets"] = datasets

        return render(request, "data.html", context)

def labels(request):
    return render(request, "labels.html",)


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
