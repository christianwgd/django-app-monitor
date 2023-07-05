from django import template

from app.models import ProcessMetric

register = template.Library()


@register.filter
def label(arg):
    return ProcessMetric._meta.get_field(arg).verbose_name