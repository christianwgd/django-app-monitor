from django.contrib import admin

from app.models import Application, ProcessMetric


@admin.register(Application)
class ApplicationPostAdmin(admin.ModelAdmin):
    list_display = ['name']
    autocomplete_fields = ['admins']


@admin.register(ProcessMetric)
class ProcessMetricAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'cpu_time', 'cpu_percent', 'mem_rss', 'mem_percent']
