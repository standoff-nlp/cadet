import os
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from colorful.fields import RGBColorField
from django.conf import settings
from pathlib import Path




class SpacyLanguage(models.Model):
    language = models.TextField(unique=True)
    iso = models.CharField(max_length=2, blank=True, null=True)
    is_core = models.NullBooleanField(blank=True)
    import_from_spacy_core = models.NullBooleanField(blank=True) # Each project has a new language object, it can be a cloned version of core, but it is custom

    def get_lang_dir(self):
        path = settings.CUSTOM_LANGUAGES_DIRECTORY + '/lang/' + self.language
        if not os.path.exists(path):
            os.makedirs(path)

    stop_words = models.FilePathField(path=get_lang_dir, match ="stop_words.py",  
              recursive = False, null=True)



    def get_lookups_dir(self):
        path = settings.CUSTOM_LANGUAGES_DIRECTORY + '/lookups-data/' + self.language
        if not os.path.exists(path):
            os.makedirs(path)

    lemma_exc = models.FilePathField(path=get_lookups_dir, match ="*_lemma_exc.json",  
              recursive = False, null=True)
    lemma_index = models.FilePathField(path=get_lookups_dir, match ="*_lemma_index.json",  
              recursive = False, null=True)
    lemma_lookup = models.FilePathField(path=get_lookups_dir, match ="*_lemma_lookup.json",  
              recursive = False, null=True)
    lemma_rules = models.FilePathField(path=get_lookups_dir, match ="*_lemma_rules.json",  
              recursive = False, null=True)

    def update(self):
        if self.import_from_spacy_core:
            # TODO import data from core lookups-data and lang
            self.import_from_spacy_core = None
            self.save()

        # TODO check if custom lang paths exist, if not create
        custom_lang = settings.CUSTOM_LANGUAGES_DIRECTORY + '/lang/' + self.language
        custom_lang = Path(custom_lang)

        spacy_path = Path(spacy.__file__.replace('__init__.py',''))
        spacy_lang = spacy_path / 'lang'
        sym_path = spacy_lang / self.language
        if not sym_path.exists():
            os.symlink(custom_lang, str(spacy_lang))
    

    def auto_suggest_lemma():
        # Method used in annotation UI, given token text, will find and suggest closest lemma in the dict
        pass

    def __str__(self):
        if self.language:
            return f"{self.iso} - {self.language}"
        if self.iso == "xx":
            return f"{self.iso} - Multilingual"
        else:
            return f"{self.iso}"
    

class Project(models.Model):
    title = models.CharField(max_length=220, blank=True, null=True)
    project_slug = models.SlugField(max_length=140, default=None)
    owners = models.ManyToManyField(User, related_name="owners")
    editors = models.ManyToManyField(User, related_name="editors")
    annotators = models.ManyToManyField(User, related_name="annotators", blank=True)
    spacy_language = models.ForeignKey(
        SpacyLanguage, on_delete=models.CASCADE, blank=True, null=True
    )
    description = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=220, blank=True, null=True)
    label_set = models.ForeignKey(
        "LabelSet", on_delete=models.CASCADE, blank=True, null=True
    )

    NO_REVIEW = "NR"
    SINGLE = "SR"
    MULTI = "MR"

    REVIEW_CHOICES = [
        (NO_REVIEW, "No review required"),
        (SINGLE, "Single required"),
        (MULTI, "Multiple annotators"),
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
    language = models.CharField(max_length=220, blank=True, null=True)
    
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
