import markdown as md
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='markdown')
@stringfilter
def markdown(value):
    return mark_safe(
        md.markdown(
            value,
            extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.tables',
                'markdown.extensions.nl2br',
            ],
        )
    )


@register.filter(name='strip')
@stringfilter
def strip_whitespace(value):
    return value.strip()
