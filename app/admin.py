from django.contrib import admin

from app.models import Application, ProcessMetric


@admin.register(Application)
class ApplicationPostAdmin(admin.ModelAdmin):
    list_display = ['name']
    autocomplete_fields = ['admins']


@admin.register(ProcessMetric)
class ProcessMetricAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'app', 'cpu_time', 'mem_rss']
    list_filter = ['app']
