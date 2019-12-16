from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField




class SpacyLanguage(models.Model):
    language = models.TextField(blank=True, null=True)
    iso = models.CharField(max_length=2, blank=True, null=True)

    def __str__(self):
        if self.language:
            return f"{self.iso} - {self.language}"
        if self.iso == "xx":
            return f"{self.iso} - Multilingual"
        else:
            return f"{self.iso}"


class Project(models.Model):
    title = models.CharField(max_length=220, blank=True, null=True)
    owners = models.ManyToManyField(User, related_name="owners")
    editors = models.ManyToManyField(User, related_name="editors")
    annotators = models.ManyToManyField(User, related_name="annotators", blank=True)
    description = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=220, blank=True, null=True)
    datasets = models.ManyToManyField("DataSet", blank=True, default=None)

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


class Dataset(models.Model):  # TODO Remove, redundant with Project
    title = models.CharField(max_length=220, blank=True, null=True)
    texts = models.ManyToManyField("Text")
    language = models.CharField(max_length=220, blank=True, null=True)
    spacy_language = models.ForeignKey(
        SpacyLanguage, on_delete=models.CASCADE, blank=True, null=True
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    source = models.URLField(max_length=1000, blank=True)
    strategic_anno = models.NullBooleanField(blank=True)

    def __str__(self):
        return f"{self.title}"


class Text(models.Model):
    text = models.TextField(blank=True, null=True)
    datasets = models.ManyToManyField("DataSet", blank=True)

    def __str__(self):
        return f"{self.id}"

class LabelSet(models.Model):
    title = models.CharField(max_length=220, blank=True, null=True)
    groups = models.ManyToManyField("LabelGroup")
    group_order = ArrayField(models.CharField(max_length=200), blank=True)

    def __str__(self):
        return f"{self.title}"

class LabelGroup(models.Model):
    title = models.CharField(max_length=220, blank=True, null=True)
    labels = models.ManyToManyField("Label")

    def __str__(self):
        return f"{self.title}"


class Label(models.Model):
    label = models.CharField(max_length=220, blank=True, null=True)
    values = models.ManyToManyField("Value")
    shortcut_key = models.CharField(max_length=220, blank=True, null=True)
    color = models.CharField(max_length=220, blank=True, null=True)

    def __str__(self):
        if self.value:
            return f"{self.label}:{self.value}"
        else:
            return f"{self.label}"


class Value(models.Model):
    value = models.CharField(max_length=220, blank=True, null=True)

    def __str__(self):
        return f"{self.value}"


class AnnotationType(models.Model):
    name = models.CharField(max_length=220)

    def __str__(self):
        return f"{self.name}"


class Annotation(models.Model):
    annotation_type = models.ForeignKey(
        AnnotationType, on_delete=models.CASCADE, default=None
    )
    annotation_text = models.TextField(blank=True, null=True)
    labels = models.ManyToManyField(Label)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    dataset = models.ForeignKey("DataSet", on_delete=models.CASCADE, default=None)
    text = models.ForeignKey(
        Text, on_delete=models.CASCADE, related_name="annotation_text"
    )

    start_char = models.IntegerField(default=None)

    end_char = models.IntegerField(default=None)

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="annotation_author"
    )
    approved = models.BooleanField(default=None)
    auto_generated = models.BooleanField(default=None)

    def end_char(self):
        return self.start_char + len(self.annotation_text)

    def __str__(self):
        return f"{self.id}"
