from django.forms import (
    ModelForm,
    FileField,
    ModelChoiceField,
    ModelMultipleChoiceField,
    Textarea,
    CheckboxInput,
)
from cadet_app.models import (
    Project,
    Text,
    SpacyLanguage,
    AnnotationType,
    Annotation,
    Label,
    Attribute,
)
from django_select2.forms import Select2Widget, Select2TagWidget, Select2MultipleWidget
from colorful.widgets import ColorFieldWidget


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        exclude = ("project_slug","spacy_language","label_set","language")
        fields = "__all__"

        widgets = {
            "owners": Select2Widget,
            "editors": Select2MultipleWidget,
            "annotators": Select2MultipleWidget,
        }

class ProjectLanguageForm(ModelForm):
    class Meta:
        model = Project
        exclude = ("project_slug","label_set","language")
        fields = "__all__"

        widgets = {
            "spacy_language": Select2TagWidget,
            
        }


class TextForm(ModelForm):
    file = FileField()
    spacy_language = ModelChoiceField(
        queryset=SpacyLanguage.objects.all().order_by("iso"),
        empty_label="(none)",
        required=False,
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
        widgets = {
            "color": ColorFieldWidget,
        }


class AnnotationForm(ModelForm):
    def __init__(self, *args, **kwargs):

        self.project = kwargs.pop("project")
        super(AnnotationForm, self).__init__(*args, **kwargs)
        project_obj = Project.objects.get(id=self.project)

        for label_group in project_obj.label_set.groups.all():
            self.fields[label_group.title + "_label"] = ModelChoiceField(
                queryset=label_group.labels.all(), widget=Select2TagWidget,
            )
            # TODO add check if the labels have attributes, don't add field unless they do
            self.fields[label_group.title + "_attrib"] = ModelMultipleChoiceField(
                queryset=Attribute.objects.all(),  # TODO write query to limit for labels in label_group and just their attrib
                widget=Select2MultipleWidget,
            )
            self.fields["annotation_type"] = ModelChoiceField(
                queryset=AnnotationType.objects.all(), widget=Select2TagWidget,
            )
        # self.fields['location'].widget = RelatedFieldWidgetWrapper(self.fields['location'].widget, rel, self.admin_site)

    class Meta:
        model = Annotation
        fields = "__all__"
        exclude = (
            "author",
            "annotation_text",
            "labels",
            "project",
            "text",
            "start_char",
            "end_char",
            "approved",
            "auto_generated",
        )


class EditAnnotationForm(ModelForm):
    def __init__(self, *args, **kwargs):

        self.project = kwargs.pop("project")
        self.user = kwargs.pop('user', None)
        super(EditAnnotationForm, self).__init__(*args, **kwargs)
        project_obj = Project.objects.get(id=self.project)
        

        for label_group in project_obj.label_set.groups.all():
            self.fields[label_group.title + "_label"] = ModelChoiceField(
                queryset=label_group.labels.all(), widget=Select2TagWidget,
            )
            # TODO add check if the labels have attributes, don't add field unless they do
            self.fields[label_group.title + "_attrib"] = ModelMultipleChoiceField(
                queryset=Attribute.objects.all(),  # TODO write query to limit for labels in label_group and just their attrib
                widget=Select2MultipleWidget,
            )
            self.fields["annotation_type"] = ModelChoiceField(
                queryset=AnnotationType.objects.all(), widget=Select2TagWidget,)


    class Meta:
        model = Annotation
        fields = "__all__"
        exclude = (
            "author",
            "labels",
            "project",
            "text",
            "start_char",
            "end_char",
            "approved",
            "auto_generated",
        )

        widgets = {
            "auto_generated": CheckboxInput,
            "annotation_type": Select2Widget,
            "project": Select2Widget,
            'annotation_text': Textarea(attrs={'rows':1, 'cols':27}),
        }
      