from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "index.html",)

def projects(request):
    return render(request, "projects.html",)

def data(request):
    return render(request, "data.html",)

def labels(request):
    return render(request, "labels.html",)

def annotate(request):
    return render(request, "annotate.html",)
    
def export(request):
    return render(request, "export.html",)


