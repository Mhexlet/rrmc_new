from django import template
from django.conf import settings


register = template.Library()


@register.filter(name='file_name')
def file_name(path):
    return path.split('/')[-1]