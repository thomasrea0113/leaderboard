from typing import TYPE_CHECKING
from itertools import product
from django.forms.models import ModelMultipleChoiceField
from django.urls.resolvers import get_resolver
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.forms import ModelForm
from django.urls import path
from django.shortcuts import redirect

from . import models

resolve = get_resolver().resolve

if TYPE_CHECKING:
    from typing import Any, List, Optional, Dict
    from django.db.models.options import Options
    from django.db.models.query import QuerySet
    from django.http import HttpRequest
    from django.urls.resolvers import URLPattern


@admin.register(models.AgeDivision)
class AgeDivisionAdmin(admin.ModelAdmin):
    pass


@admin.register(models.BoardDefinition)
class BoardDefinitionAdmin(admin.ModelAdmin):
    pass


class AddManyBoardsForm(ModelForm):
    board_definitions = ModelMultipleChoiceField(
        queryset=models.BoardDefinition.objects.all())
    divisions = ModelMultipleChoiceField(
        queryset=models.AgeDivision.objects.all())
    weight_classes = ModelMultipleChoiceField(
        queryset=models.WeightClass.objects.all())

    instance: 'models.Board'

    class Meta:
        model = models.Board
        fields = []

    def clean(self):
        cleaned = super().clean()
        # TODO find a better way to do this... likely involving a custom implementation of ModelForm
        # because we hacked a ModelForm to use it to generate multiple objects, the model fields
        # aren't set. Because board_defnition is required, we must manually set it to the first
        # selected board defition. The instance never actually get's saved,
        self.instance.board_definition = self.cleaned_data.get(
            'board_definitions', [None])[0]
        self.instance.division = self.cleaned_data.get(
            'divisions', [None])[0]
        self.instance.weight_class = self.cleaned_data.get(
            'weight_classes', [None])[0]
        return cleaned

    def save(self, commit: 'bool' = ...) -> 'List[models.Board]':
        definitions: 'QuerySet[models.BoardDefinition]' = self.cleaned_data['board_definitions']
        divisions: 'QuerySet[models.AgeDivision]' = self.cleaned_data['divisions']
        weight_classes: 'QuerySet[models.WeightClass]' = self.cleaned_data['weight_classes']

        boards: 'List[models.Board]' = []
        for definition, division, weight_class in product(definitions, divisions, weight_classes):
            board = models.Board()
            board.board_definition = definition
            board.division = division
            board.weight_class = weight_class
            boards.append(board)

        created: 'List[models.Board]' = models.Board.objects.bulk_create(
            boards, ignore_conflicts=True)

        return created


@admin.register(models.Board)
class BoardAdmin(admin.ModelAdmin):
    add_many_help = _('''For convenience, this page allows you to add many boards at once.
Here, you are able to select any combination of board definitions/weight classes, and divisions.
Then, we will permiate all the possible combinations of those selected fields. For example, if
you select 2 board definitions, 1 weight class, and 2 divisions, 2x2x1=4 boards will be created.''')

    @property
    def my_urls(self) -> 'List[URLPattern]':
        return [
            path('add-many/', view=self.add_many_view,
                 name=self.url_pattern('add-many'))
        ]

    def url_pattern(self, route: 'str'):
        return f'{self.opts.app_label}_{self.opts.model_name}_{route}'

    def is_route(self, request: 'HttpRequest', route: 'str') -> bool:
        return resolve(request.path_info).url_name == self.url_pattern(route)

    def is_custom_route(self, request: 'HttpRequest'):
        return resolve(request.path_info).url_name in [r.name for r in self.my_urls]

    def get_form(self, request: 'HttpRequest',
                 obj: 'Optional[models.Board]' = ...,
                 change: 'bool' = ..., **kwargs: 'Any'):
        if self.is_custom_route(request):
            return AddManyBoardsForm
        return super().get_form(request, obj=obj, change=change, **kwargs)

    # pylint: disable=too-many-arguments
    def render_change_form(self, request: 'HttpRequest', context: 'Dict[str,Any]',
                           add: 'bool' = False, change: 'bool' = False,
                           form_url: 'str' = '', obj: 'models.Board' = None):
        if self.is_route(request, 'add-many'):
            # render_change_form will set opts in the super call, but we need it now
            opts: 'Options[models.Board]' = self.model._meta
            context['adminform'].fieldsets[0][1]['description'] = self.add_many_help
            context.update({
                'title': f'Add Many {opts.verbose_name_plural}'
            })
        return super().render_change_form(request, context, add, change, form_url, obj)

    def add_many_view(self, request: 'HttpRequest', *args, **kwargs):

        # leverage the existing add_view to render the form (overriden in get_form)
        if request.method == 'GET':
            return self.add_view(request, *args, **kwargs)

        # on post, the add_view does a lot of stuff that we don't need. Instead, simply
        # create the boards and
        form = AddManyBoardsForm(request.POST)

        # conveniently, the default view will also handle form errors quite nicely.
        if not form.is_valid():
            return self.add_view(request, *args, **kwargs)

        created = form.save()
        model_name = self.opts.verbose_name_plural if created != 1 else self.opts.verbose_name
        self.message_user(request, f'{len(created)} new {model_name} created')
        return redirect('admin:' + self.url_pattern('changelist'))

    def get_urls(self) -> 'List[URLPattern]':
        return self.my_urls + super().get_urls()


@admin.register(models.WeightClass)
class WeightClassAdmin(admin.ModelAdmin):
    pass
