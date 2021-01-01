from typing import TYPE_CHECKING
from django.forms import Widget
from django.contrib import admin

if TYPE_CHECKING:
    from typing import Any
    from django.contrib.admin.sites import AdminSite
    from django.db.models.query import QuerySet
    from django.db.models.options import Options
    from django.forms.renderers import BaseRenderer
    from django.utils.safestring import SafeText


class ModelChangeListWidget(Widget):
    template_name = 'admin/includes/model_link_list.html'

    def __init__(self,
                 admin_site: 'AdminSite|None' = None,
                 attrs: 'dict[str, Any]|None' = None) -> None:
        super().__init__(attrs=attrs)
        self.admin_site = admin_site

    def get_url_name(self, value: 'QuerySet'):
        meta: 'Options' = value.model._meta
        return f'{self.admin_site.name}:{meta.app_label}_{meta.model_name}_change'

    def get_context(self, name: str, value: 'QuerySet', attrs) -> 'dict[str, Any]':
        context = super().get_context(name, value, attrs)
        context.update({
            'url_name': self.get_url_name(value),
            'admin_site': self.admin_site or admin.site})
        return context

    # don't do anything to the value - we just want the queryset not a str
    def format_value(self, value):
        return value

    # here just to enforce the value type
    def render(self, name: 'str', value: 'QuerySet',
               attrs: 'dict[str, Any]|None' = None,
               renderer: 'BaseRenderer|None' = None) -> 'SafeText':
        return super().render(name, value, attrs=attrs, renderer=renderer)
