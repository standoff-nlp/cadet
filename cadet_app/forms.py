from django.forms import ModelForm
from cadet_app.models import Project

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = '__all__'