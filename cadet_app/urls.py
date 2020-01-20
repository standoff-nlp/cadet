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
    path("language/", views.language, name="language"),
    path("language/stop_words", views.stop_words, name="stop_words"),
    path("language/examples", views.examples, name="examples"),
    path("language/tokenization", views.tokenization, name="tokenization"),
    path("language/lemmata", views.lemmata, name="lemmata"),
    path("set_text/<id>", views.set_text, name="set_text"),
    path("edit_text/<id>", views.edit_text, name="edit_text"),
    path("delete_text/<id>", views.delete_text, name="delete_text"),
    path(
        "edit_annotation_type/<id>",
        views.edit_annotation_type,
        name="edit_annotation_type",
    ),
    path("add_annotation_type/", views.add_annotation_type, name="add_annotation_type"),
    path(
        "add_annotation_form/<id>",
        views.add_annotation_form,
        name="add_annotation_form",
    ),
    path("edit_annotation/<id>", views.edit_annotation, name="edit_annotation"),
    path("edit_annotation/", views.edit_annotation_no_id, name="edit_annotation"),
    path("data/", views.data, name="data"),
    path("labels/", views.labels, name="labels"),
    path("set_labelset/<id>", views.set_labelset, name="set_labelset"),
    path("annotate/", views.annotate, name="annotate"),
    path("annotate/<project>/", views.annotate, name="annotate"),
    path("annotate/<project>/<text>", views.annotate, name="annotate"),
    path("export/", views.export, name="export"),
]
