from django.contrib import admin

from .models import MarFile, LanguageFile, UpdateChannel, Release, PartialUpdate, PartialLanguageUpdate

admin.site.register(MarFile)
admin.site.register(LanguageFile)
admin.site.register(UpdateChannel)
admin.site.register(Release)
admin.site.register(PartialUpdate)
admin.site.register(PartialLanguageUpdate)
