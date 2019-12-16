from django.contrib import admin
from cadet_app.models import *

class ProjectAdmin(admin.ModelAdmin):
    pass
admin.site.register(Project, ProjectAdmin)

class DatasetAdmin(admin.ModelAdmin):
    pass
admin.site.register(Dataset, DatasetAdmin)

class TextAdmin(admin.ModelAdmin):
    pass
admin.site.register(Text, TextAdmin)

class AnnotationAdmin(admin.ModelAdmin):
    pass
admin.site.register(Annotation, AnnotationAdmin)

class AnnotationTypeAdmin(admin.ModelAdmin):
    pass
admin.site.register(AnnotationType, AnnotationTypeAdmin)

