from django import template

from app.models import SystemMetric

register = template.Library()


@register.filter
def label(arg):
    return SystemMetric._meta.get_field(arg).verbose_name


@register.simple_tag
def http_status_color(value):
    if value == 200:
        return 'success'
    return 'danger'


@register.simple_tag
def health_check_color(value):
    if value == 'working':
        return 'success'
    return 'danger'


@register.simple_tag
def metrics_color(app, value_type):
    value = getattr(app.metrics.latest('timestamp'), value_type)
    threshold_name = f'max_{value_type}'
    if hasattr(app, threshold_name):
        threshold = getattr(app, threshold_name)
        if value > threshold:
            return 'danger'
        return 'success'
    return 'default'


@register.simple_tag
def metrics_icon(app, value_type):
    value = getattr(app.metrics.latest('timestamp'), value_type)
    threshold_name = f'max_{value_type}'
    if hasattr(app, threshold_name):
        threshold = getattr(app, threshold_name)
        if value > threshold:
            return 'exclamation-circle-fill'
        return 'check-circle-fill'
    return None
