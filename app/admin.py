from django.contrib import admin

from app.models import Application


@admin.register(Application)
class ApplicationPostAdmin(admin.ModelAdmin):
    list_display = ['name']
    autocomplete_fields = ['admins']
