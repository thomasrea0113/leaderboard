from typing import TYPE_CHECKING
from django.contrib import admin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.forms import Form
from django.forms.models import ModelForm
from django.urls import path
from django.views.generic import FormView

from . import models

if TYPE_CHECKING:
    from typing import Any, List, Dict
    from django.contrib.admin.sites import AdminSite
    from django.urls.resolvers import URLPattern
    from django.http import HttpRequest, HttpResponse
    from django.core.handlers.wsgi import WSGIRequest


@admin.register(models.AgeDivision)
class AgeDivisionAdmin(admin.ModelAdmin):
    pass


@admin.register(models.BoardDefinition)
class BoardDefinitionAdmin(admin.ModelAdmin):
    pass


class AddManyBoardsForm(ModelForm):
    class Meta:
        model = models.Board
        fields = ['board_definition']


@admin.register(models.Board)
class BoardAdmin(admin.ModelAdmin):
    # need to wrap the class-based view so that we can include extra
    # context parameters form the outer scope
    def add_many_view(self, request: 'WSGIRequest'):
        site: 'AdminSite' = admin.site
        return self.AddManyView.as_view()(request,
                                          title='Add Many Boards',
                                          opts=self.opts,
                                          is_nav_sidebar_enabled=True,
                                          has_permission=self.has_add_permission(
                                              request),
                                          site_url=site.site_url,
                                          available_apps=site.get_app_list(request))

    class AddManyView(PermissionRequiredMixin, FormView):
        template_name = 'admin/divisions/board/add_many.html'
        form_class = AddManyBoardsForm

        ctx: 'Dict[str, Any]' = {}

        def has_permission(self) -> bool:
            return self.ctx['has_permission']

        def dispatch(self, request: 'HttpRequest', *args: 'Any', **kwargs: 'Any') -> 'HttpResponse':
            self.ctx.update(**kwargs)
            return super().dispatch(request, *args, **kwargs)

        def get_context_data(self, **kwargs):
            kwargs.update(self.ctx)
            return super().get_context_data(**kwargs)

    def get_urls(self) -> 'List[URLPattern]':
        add_many_name = f'{self.opts.app_label}_{self.opts.model_name}_add-many'
        urls = [
            path('add-many/', view=self.add_many_view,
                 name=add_many_name)
        ] + super().get_urls()
        return urls


@admin.register(models.WeightClass)
class WeightClassAdmin(admin.ModelAdmin):
    pass
