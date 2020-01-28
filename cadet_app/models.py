import os
import spacy
from pathlib import Path
from django.conf import settings
import json
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from colorful.fields import RGBColorField

def get_compatible_models():
    spacy_version = spacy.__version__
    compatibility = Path(settings.CUSTOM_LANGUAGES_DIRECTORY + '/core_models/compatibility.json')
    with open(str(compatibility)) as file:
        data = json.load(file)
        compatible_models = data['spacy'][spacy_version].keys()
        compatible_models = [(model,model) for model in compatible_models] # choices requires a tuple
        compatible_models.append(('None','None'))
    return compatible_models    

class SpacyLanguage(models.Model):
    language = models.TextField(unique=True)
    slug = models.SlugField(max_length=140, default=None)
    iso = models.CharField(max_length=2, blank=True, null=True)
    is_core = models.NullBooleanField(blank=True)

  
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.language)
        
        if self.is_core: # Core objects are added with manage.py setup from spacy/lang # TODO add condition in setup to ignore symlinks
            super().save(*args, **kwargs)
        else:
            #create_custom_spacy_language_object(self.language)
            super().save(*args, **kwargs)

    def auto_suggest_lemma():
        # Method used in annotation UI, given token text, will find and suggest closest lemma in the dict
        pass

    

    def __str__(self):
        return f"{self.language}"
    

class Project(models.Model):
    title = models.CharField(max_length=220, blank=True, null=True)
    project_slug = models.SlugField(max_length=140, default=None)
    owners = models.ManyToManyField(User, related_name="owners")
    editors = models.ManyToManyField(User, related_name="editors")
    annotators = models.ManyToManyField(User, related_name="annotators", blank=True)
    spacy_language = models.ForeignKey(
        SpacyLanguage, on_delete=models.CASCADE, blank=True, null=True
    )
    core_model = models.CharField(max_length=220,choices=get_compatible_models(), default="None")

    description = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=220, blank=True, null=True)
    label_set = models.ForeignKey(
        "LabelSet", on_delete=models.CASCADE, blank=True, null=True
    )

    NO_REVIEW = "NR"
    SINGLE = "SR"
    TWO = "3"
    THREE = "4"

    REVIEW_CHOICES = [
        (NO_REVIEW, "No review required"),
        (SINGLE, "Editor approval"),
        (TWO, "two annotator consensus"),
        (THREE, "three annotator consensus"),
    ]
    review = models.CharField(max_length=2, choices=REVIEW_CHOICES, default=NO_REVIEW,)

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        if not self.project_slug:
            self.project_slug = slugify(self.title)
        super().save(*args, **kwargs)

        if not self.spacy_language:
            pass
            # TODO create self.spacy_language = create_spacy_language(self.language)

class Text(models.Model):
    title = models.CharField(max_length=220, blank=True, null=True)
    text_slug = models.SlugField(max_length=140, default=None)
    text = models.TextField(blank=True, null=True)
    standoff = models.TextField(blank=True, null=True)
    projects = models.ManyToManyField(
        "Project", blank=True, related_name="text_project"
    )
    language = models.CharField(max_length=220, blank=True, null=True) #TODO remove, language is set in project.spacy_language
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    source = models.URLField(max_length=1000, blank=True)
    strategic_anno = models.NullBooleanField(blank=True)
    window_default = models.IntegerField(
        default=200,
        help_text="Default number of charachters displayed in the annotation window",
    )

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        if not self.text_slug:
            self.text_slug = slugify(self.title)
        super().save(*args, **kwargs)


class LabelSet(models.Model):
    title = models.CharField(max_length=220, blank=True, null=True)
    groups = models.ManyToManyField("LabelGroup")
    group_order = ArrayField(models.CharField(max_length=200), blank=True, null=True)

    def __str__(self):
        return f"{self.title}"


class LabelGroup(models.Model):
    title = models.CharField(max_length=220, blank=True, null=True)
    labels = models.ManyToManyField("Label", blank=True,)
    explain = models.CharField(
        max_length=220,
        blank=True,
        null=True,
        help_text="Explaination of the label group and its use",
    )

    def __str__(self):
        return f"{self.title}"



class Label(models.Model):
    name = models.CharField(max_length=220, blank=True, null=True)
    human_name = models.CharField(max_length=220, blank=True, null=True)
    explain = models.CharField(
        max_length=220,
        blank=True,
        null=True,
        help_text="Explaination of the label and its use",
    )
    explain_link = models.URLField(max_length=1000, blank=True)
    attributes = models.ManyToManyField("Attribute", blank=True,)
    shortcut_key = models.CharField(max_length=220, blank=True, null=True)
    color = models.CharField(max_length=220, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class Attribute(models.Model):
    key = models.CharField(max_length=220, blank=True, null=True)
    value = models.CharField(max_length=220, blank=True, null=True)
    key_shortcut_key = models.CharField(max_length=220, blank=True, null=True)
    value_shortcut_key = models.CharField(max_length=220, blank=True, null=True)

    def __str__(self):
        try:
            return f"{self.key}: {self.value}"
        except:
            return f"{self.key}"


class AnnotationType(models.Model):
    name = models.CharField(max_length=220, blank=True, null=True)
    color = RGBColorField(default="#FF0000", blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class Annotation(models.Model):
    """An annotation is the core entity for the annotation applications.  An annotation has a type, and can be 
    a token, a span, a sentence or other type.  It contains a relation to a project and text, which provide a 
    unique locator.  There is a m2m link to Label, which provides all labels associated with the token. 
    """
    def get_token_id():
        try:
            return AnnotationType.objects.get(name="token").pk
        except:
            return None

    annotation_type = models.ForeignKey(
        AnnotationType, on_delete=models.CASCADE, default=get_token_id
    )
    annotation_text = models.TextField(blank=True, null=True)
    labels = models.ManyToManyField(Label, blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    text = models.ForeignKey(
        Text, on_delete=models.CASCADE, related_name="annotation_text", blank=True, null=True
    )

    start_char = models.IntegerField(default=None, null=True)

    end_char = models.IntegerField(default=None, null=True)

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="annotation_author"
    )
    approved = models.BooleanField(default=None, null=True)
    auto_generated = models.BooleanField(default=None, null=True)

    def __str__(self):
        return f"{self.id}-{self.annotation_type}"
