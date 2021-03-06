from django.contrib import admin
from cadet_app.models import *


class AttributeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Attribute, AttributeAdmin)


class ProjectAdmin(admin.ModelAdmin):
    pass


admin.site.register(Project, ProjectAdmin)


class TextAdmin(admin.ModelAdmin):
    pass


admin.site.register(Text, TextAdmin)


class AnnotationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "annotation_type",
        "annotation_text",
        "text",
        "created_at",
    )
    list_filter = (
        "project",
        "annotation_type",
        "text",
    )


admin.site.register(Annotation, AnnotationAdmin)


class AnnotationTypeAdmin(admin.ModelAdmin):
    pass


admin.site.register(AnnotationType, AnnotationTypeAdmin)


class LabelAdmin(admin.ModelAdmin):
    search_fields = ['name']


admin.site.register(Label, LabelAdmin)


class LabelSetAdmin(admin.ModelAdmin):
    pass


admin.site.register(LabelSet, LabelSetAdmin)


class LabelGroupAdmin(admin.ModelAdmin):
    pass


admin.site.register(LabelGroup, LabelGroupAdmin)

class SpacyLanguageAdmin(admin.ModelAdmin):
    pass


admin.site.register(SpacyLanguage, SpacyLanguageAdmin)