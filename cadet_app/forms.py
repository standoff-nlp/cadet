from django.forms import ModelForm, FileField, ModelChoiceField
from cadet_app.models import Project, Dataset, SpacyLanguage

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

class DatasetForm(ModelForm):
    file = FileField()
    spacy_language = ModelChoiceField(queryset=SpacyLanguage.objects.all().order_by('iso'), empty_label="(none)")
    class Meta:
        model = Dataset
        fields = ['file','title', 'language','source']