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
    path("login/", views.site_login, name="login"),
    path("logout/", views.site_logout, name="logout"),
    path("projects/", views.projects, name="projects"),
    path("add_project/", views.add_project, name="add_project"),
    path("edit_project/<id>", views.edit_project, name="edit_project"),
    path("set_project/<id>", views.set_project, name="set_project"),
    path("set_text/<id>", views.set_text, name="set_text"),
	path("edit_text/<id>", views.edit_text, name="edit_text"),
	path("delete_text/<id>", views.delete_text, name="delete_text"),
    
    path("data/", views.data, name="data"),
    path("labels/", views.labels, name="labels"),
    path("annotate/", views.annotate, name="annotate"),
    path("annotate/<project>/", views.annotate, name="annotate"),
    path("annotate/<project>/<text>", views.annotate, name="annotate"),
    path("export/", views.export, name="export"),
    
]
