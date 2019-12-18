from django.forms import ModelForm, FileField, ModelChoiceField, ModelMultipleChoiceField
from cadet_app.models import Project, Text, SpacyLanguage, AnnotationType, Annotation, Label
from django_select2.forms import Select2Widget, Select2MultipleWidget


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        exclude = ("project_slug",)
        fields = "__all__"


class TextForm(ModelForm):
    file = FileField()
    spacy_language = ModelChoiceField(
        queryset=SpacyLanguage.objects.all().order_by("iso"), empty_label="(none)"
    )

    class Meta:
        model = Text
        fields = [
            "file",
            "title",
            "language",
            "source",
            "spacy_language",
            "strategic_anno",
        ]


class AnnotationTypeForm(ModelForm):
    class Meta:
        model = AnnotationType
        fields = "__all__"


class AnnotationForm(ModelForm):
    class Meta:
        model = Annotation
        fields = ["annotation_type","labels",]
        widgets = { 'labels': Select2MultipleWidget }
