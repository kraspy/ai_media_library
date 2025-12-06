import markdown as md
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter()
@stringfilter
def markdown(value):
    return md.markdown(value, extensions=['markdown.extensions.fenced_code'])


@register.filter(name='strip')
@stringfilter
def strip_whitespace(value):
    return value.strip()
