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
    path("data/", views.data, name="data"),
    path("labels/", views.labels, name="labels"),
    path("annotate0/", views.annotate0, name="annotate0"),
    path("annotate0/<int:project>/<int:text>/<int:sentence>/<int:token>", views.annotate0, name="annotate0"),
    path("annotate1/", views.annotate1, name="annotate1"),
    path("export/", views.export, name="export"),
    
]
