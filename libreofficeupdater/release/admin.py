from django.contrib import admin

from .models import MarFile, LanguageFile, UpdateChannel, Release

admin.site.register(MarFile)
admin.site.register(LanguageFile)
admin.site.register(UpdateChannel)
admin.site.register(Release)
