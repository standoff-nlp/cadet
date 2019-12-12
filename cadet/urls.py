"""cadet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.urls import include
from annotator_store import views as annotator_views
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cadet_app.urls')),
    path('', include('social_django.urls', namespace='social'))
]

urlpatterns += [
    # annotations
    path('store/annotations/', include('annotator_store.urls', namespace='annotation-api')),
    # annotatorjs doesn't handle trailing slash in api prefix url
    path('store/annotations', annotator_views.AnnotationIndex.as_view(), name='annotation-api-prefix'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
