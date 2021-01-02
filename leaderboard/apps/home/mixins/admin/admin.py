from apps.home.widgets.admin import ModelChangeListWidget
from typing import Generic, TYPE_CHECKING, TypedDict
from django.shortcuts import redirect
from django.urls.resolvers import get_resolver
from django.urls import path
from django.utils.translation import gettext_lazy as _

resolve = get_resolver().resolve

if TYPE_CHECKING:
    from typing import Sequence, Any, Type, Optional, List, Dict
    from django.contrib.admin import ModelAdmin
    from django.contrib.admin.options import _ModelT
    from django.http.request import HttpRequest
    from django.urls.resolvers import URLPattern
    from django.forms import ModelForm
    from django.template.response import TemplateResponse
    _Base = ModelAdmin
else:
    _Base = object

# There's a bug in pylint atm, should be fixed soon - https://github.com/PyCQA/pylint/issues/3876
# pylint: disable=inherit-non-class


class CustomAdminPageBase(TypedDict):
    name: 'str'
    form_class: 'Type[ModelForm]'


class CustomAdminPage(CustomAdminPageBase, total=False):
    help_text: 'str'
    route: 'str'
    context: 'Dict[str, Any]'


class CustomActionFormMixin(_Base):
    custom_pages: 'Sequence[CustomAdminPage]'

    def url_pattern(self, route: 'str'):
        return f'{self.opts.app_label}_{self.opts.model_name}_{route}'

    def is_route(self, request: 'HttpRequest', route: 'str') -> bool:
        return resolve(request.path_info).url_name == self.url_pattern(route)

    def get_page_options(self, request: 'HttpRequest') -> 'Optional[CustomAdminPage]':
        route_name = self.get_route_name(request)

        if route_name:
            def _filter(options: 'CustomAdminPage'):
                return route_name == self.url_pattern(options['name'])

            return next(filter(_filter, self.custom_pages), None)

        return None

    # pylint: disable=no-self-use
    def get_route_name(self, request: 'HttpRequest') -> 'Optional[str]':
        return resolve(request.path_info).url_name

    # pylint: disable=no-self-use
    def get_page_context(self, options: 'CustomAdminPage') -> 'Dict[str, Any]':
        return options.get('context', {})

    def get_form(self, request: 'HttpRequest',
                 obj: 'Optional[_ModelT]' = ...,
                 change: 'bool' = ..., **kwargs: 'Any'):
        page_options = self.get_page_options(request)
        if page_options:
            return page_options['form_class']

        return super().get_form(request, obj=obj, change=change, **kwargs)

    # pylint: disable=too-many-arguments
    def render_change_form(self, request: 'HttpRequest', context: 'Dict[str,Any]',
                           add: 'bool' = False, change: 'bool' = False,
                           form_url: 'str' = '', obj: '_ModelT' = None):
        page_options = self.get_page_options(request)
        if page_options:
            help_text = page_options.get('help_text', None)
            if help_text:
                context['adminform'].fieldsets[0][1]['description'] = _(
                    help_text)

            page_context = self.get_page_context(page_options)
            if page_context:
                context.update(page_context)

        return super().render_change_form(request, context, add, change, form_url, obj)

    def get_custom_view(self, form_type: 'Type[ModelForm]'):
        def custom_view(request: 'HttpRequest', *args, **kwargs):
            # leverage the existing add_view to render the form (overriden in get_form)
            if request.method == 'GET':
                return self.add_view(request, *args, **kwargs)

            # on post, the add_view does a lot of stuff that we don't need. Instead, simply
            # create the boards and
            form = form_type(request.POST)

            # conveniently, the default view will also handle form errors quite nicely.
            if not form.is_valid():
                return self.add_view(request, *args, **kwargs)

            self.save_custom_form(request, form)
            return redirect('admin:' + self.url_pattern('changelist'))

        return custom_view

    # pylint: disable=unused-argument
    def save_custom_form(self, request: 'HttpRequest', form: 'ModelForm'):
        return form.save()

    @property
    def custom_urls(self) -> 'List[URLPattern]':
        def get_pattern(options: 'CustomAdminPage'):
            pattern = options.get("route", options["name"])

            # explicility append the / to ensure child pages aren't added
            if pattern[-1] != '/':
                pattern += '/'

            # explicility append
            return path(pattern, view=self.get_custom_view(options['form_class']),
                        name=self.url_pattern(options['name']))

        return list(map(get_pattern, self.custom_pages))

    def get_urls(self) -> 'List[URLPattern]':
        return self.custom_urls + super().get_urls()


class AdminSelect2ListFilterMixin(_Base):
    def changelist_view(self, request: 'HttpRequest',
                        extra_context: 'Optional[Dict[str, Any]]' = None) -> 'TemplateResponse':
        ctx: 'Dict[str, Any]' = extra_context or {}
        ctx.update({'has_multiselect': True})
        return super().changelist_view(request, extra_context=ctx)
