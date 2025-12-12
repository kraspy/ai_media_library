import markdown
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
@stringfilter
def markdown_format(text):
    """
    Converts markdown text to HTML.
    Includes "fenced_code" and "tables" extensions.
    """
    return mark_safe(
        markdown.markdown(
            text,
            extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.tables',
                'markdown.extensions.nl2br',
            ],
        )
    )
