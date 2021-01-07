from typing import TYPE_CHECKING
from django.template import Library

if TYPE_CHECKING:
    from django.http import HttpRequest

register = Library()


@register.simple_tag(takes_context=True)
def query(context: 'dict', **kwargs):
    """A tag that extends the current requests query string with the provided kwargs
    """
    request: 'HttpRequest' = context['request']
    params = request.GET.copy()
    params.update(kwargs)
    return params.urlencode()
