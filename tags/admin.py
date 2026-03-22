from django.contrib import admin

from . import models


@admin.register(models.Tag)
class tagAdmin(admin.ModelAdmin):
    search_fields = ["label__istartswith"]


admin.site.register(models.TaggedItem)
