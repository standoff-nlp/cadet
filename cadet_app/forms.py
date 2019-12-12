from django.forms import ModelForm, FileField
from cadet_app.models import Project, Dataset

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

class DatasetForm(ModelForm):
    file = FileField()
    class Meta:
        model = Dataset
        fields = ['file','title', 'language','source']