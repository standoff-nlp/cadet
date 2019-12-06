from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField


class Project(models.Model):
    title = models.CharField(max_length=220, blank=True, null=True)
    image = models.ImageField()
    owners = models.ManyToManyField(User, related_name='owners')
    editors = models.ManyToManyField(User, related_name='editors')
    annotators = models.ManyToManyField(User, related_name='annotators')
    description = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=220, blank=True, null=True)
    language_object = models.CharField(max_length=220, blank=True, null=True)
    spaCy_model = models.CharField(max_length=220, blank=True, null=True)
    datasets = models.ManyToManyField("DataSet")

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


class Text(models.Model):
    text = models.TextField(blank=True, null=True)
    datasets = models.ManyToManyField('DataSet')

    def __str__(self):
        return f"{self.title}"


class Dataset(models.Model):
    title = models.CharField(max_length=220, blank=True, null=True)
    texts = models.ManyToManyField(Text)
    language = models.CharField(max_length=220, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.URLField(max_length=1000, blank=True)

    def __str__(self):
        return f"{self.title}"


class LabelGroup(models.Model):
    title = models.CharField(max_length=220, blank=True, null=True)
    labels = models.ManyToManyField("Label")

    def __str__(self):
        return f"{self.title}"


class Label(models.Model):
    label = models.CharField(max_length=220, blank=True, null=True)
    value = models.CharField(max_length=220, blank=True, null=True)
    shortcut_key = models.CharField(max_length=220, blank=True, null=True)
    color = models.CharField(max_length=220, blank=True, null=True)

    def __str__(self):
        if self.value:
            return f"{self.label}:{self.value}"
        else:
            return f"{self.label}"


class Annotation(models.Model):
    json = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    text = models.ForeignKey(Text, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    approved = models.BooleanField()

    def __str__(self):
        return f"{self.id}"
