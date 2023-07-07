from django.contrib import admin

from app.models import Application, SystemMetric


@admin.register(Application)
class ApplicationPostAdmin(admin.ModelAdmin):
    list_display = ['name']
    autocomplete_fields = ['admins']


@admin.register(SystemMetric)
class SystemMetricAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'app', 'cpu_percent', 'mem_percent']
    list_filter = ['app']
