from django.conf.urls import url
from django.urls import include, re_path
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
import cadet_app.views as views

urlpatterns = [
    path("", views.index, name="index"),
    path("projects/", views.projects, name="projects"),
    path("data/", views.data, name="data"),
    path("labels/", views.labels, name="labels"),
    path("annotate/", views.annotate, name="annotate"),
    path("export/", views.export, name="export"),
    
]
