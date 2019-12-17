from django.forms import ModelForm, FileField, ModelChoiceField
from cadet_app.models import Project, Text, SpacyLanguage, AnnotationType

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        exclude = ('project_slug',)
        fields = '__all__'

class TextForm(ModelForm):
    file = FileField()
    spacy_language = ModelChoiceField(queryset=SpacyLanguage.objects.all().order_by('iso'), empty_label="(none)")
    class Meta:
        model = Text
        fields = ['file','title', 'language','source', 'spacy_language','strategic_anno']


class AnnotationTypeForm(ModelForm):
    class Meta:
        model = AnnotationType
        fields = '__all__'
