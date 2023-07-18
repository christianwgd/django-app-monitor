from django.contrib import admin

from app.models import Application, SystemMetric, Alert


@admin.register(Application)
class ApplicationPostAdmin(admin.ModelAdmin):
    list_display = ['name']
    autocomplete_fields = ['admins']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'app', 'typus', 'value']
    list_filter = ['app', 'typus']


@admin.register(SystemMetric)
class SystemMetricAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'app', 'cpu_percent', 'mem_percent']
    list_filter = ['app']
