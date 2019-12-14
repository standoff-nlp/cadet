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

class SentenceAdmin(admin.ModelAdmin):
    pass
admin.site.register(Sentence, SentenceAdmin)

class TokenAdmin(admin.ModelAdmin):
    pass
admin.site.register(Token, TokenAdmin)