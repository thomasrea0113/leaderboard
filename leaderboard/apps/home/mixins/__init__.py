from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet

from django.http.response import JsonResponse, HttpResponse
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from django.views.generic.base import TemplateView

if TYPE_CHECKING:
    from typing import Any, Optional
    from django.http import HttpRequest
    from django.views.generic import View
    _View = View
else:
    _View = object


class LazyDjangoJSONEncoder(DjangoJSONEncoder):
    def default(self, o: 'Any') -> 'Any':
        if isinstance(o, TemplateResponse):
            return o.rendered_content
        if isinstance(o, HttpResponse):
            return o.content
        if isinstance(o, QuerySet):
            return list(o)
        return super().default(o)


class AjaxJsonResponse(JsonResponse):
    # pylint: disable=too-many-arguments
    def __init__(self, data, encoder=LazyDjangoJSONEncoder, safe=True, isJson=True,
                 json_dumps_params=None, **kwargs):
        if isinstance(data, HttpResponse):
            self.status_code = data.status_code

        super().__init__({
            'isJson': isJson,
            'content': data
        }, encoder, safe, json_dumps_params, **kwargs)


class AjaxMixin(_View):
    def dispatch(self, request: 'HttpRequest', *args: 'Any', **kwargs: 'Any') -> 'HttpResponse':
        response = super().dispatch(request, *args, **kwargs)

        if request.is_ajax() and response.status_code in range(200, 300):
            # already an appropriate response
            if isinstance(response, AjaxJsonResponse):
                return response

            # is a JsonResponse, but not an AjaxJsonResponse. Won't have the right attributes
            # that the client expects
            if isinstance(response, JsonResponse):
                raise Exception(f'''When using the {AjaxMixin}, you should return {AjaxJsonResponse}
 instead of {JsonResponse}''')

            # need to wrap the existing response
            return AjaxJsonResponse(response, isJson=False)

        return response


class DynamicHandlerMixin(_View):
    """Checks for a query parameter called 'handler', and then attempts to call a method
    in the form <method>_<handler_name>
    """

    def dispatch(self, request: 'HttpRequest', *args: 'Any', **kwargs: 'Any') -> 'HttpResponse':
        if request.method.lower() in self.http_method_names:
            handler_name = request.GET.get('handler', None)

            if not handler_name:
                return super().dispatch(request, *args, **kwargs)

            return getattr(self, f'{request.method.lower()}_{handler_name}',
                           self.http_method_not_allowed)(request, *args, **kwargs)

        return super().dispatch(request, *args, **kwargs)


class InitialTemplateView(DynamicHandlerMixin, TemplateView, metaclass=ABCMeta):
    """A view that will dynamically render a template after initial page load
    """
    template_name = 'base.html'
    initial_template: 'Optional[str]' = None

    def get_initial_context(self, request: 'HttpRequest', **kwargs) -> 'dict[str, Any]':
        kwargs.setdefault('loaded', True)
        return kwargs

    def get(self, request: 'HttpRequest', *args: 'Any', **kwargs: 'Any') -> 'HttpResponse':
        kwargs.setdefault('loaded', False)
        kwargs.setdefault('initial_template', self.initial_template)
        return super().get(request, *args, **kwargs)

    def get_initial(self, request: 'HttpRequest', *args, **kwargs):
        if self.initial_template:
            return TemplateResponse(request, self.initial_template, self.get_initial_context(request))
        raise NotImplementedError(
            'the default implementation of get_initial request that initial_template be set')
