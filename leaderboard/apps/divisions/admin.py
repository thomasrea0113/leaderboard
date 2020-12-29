from apps.home.mixins.admin.admin import CustomActionFormMixin
from typing import TYPE_CHECKING
from itertools import product
from django.forms.models import ModelMultipleChoiceField
from django.urls.resolvers import get_resolver
from django.contrib import admin
from django.forms import ModelForm

from . import models
from apps.home.mixins.admin import AdminChangeLinksMixin

resolve = get_resolver().resolve

if TYPE_CHECKING:
    from typing import Any, List, Optional, Dict, Sequence
    from django.db.models.options import Options
    from django.db.models.query import QuerySet
    from django.http import HttpRequest
    from django.template.response import TemplateResponse
    from apps.home.mixins.admin import CustomAdminPage


@admin.register(models.AgeDivision)
class AgeDivisionAdmin(admin.ModelAdmin):
    pass


@admin.register(models.BoardDefinition)
class BoardDefinitionAdmin(admin.ModelAdmin):
    pass


class AddManyBoardsForm(ModelForm):
    # base_fields will be autopopulated with the model fields. We need to remove those
    # since we're redefining them below. For other use cases, we may only want to remove
    # the fields that we redefine
    base_fields = []

    board_definitions = ModelMultipleChoiceField(
        queryset=models.BoardDefinition.objects.all())
    divisions = ModelMultipleChoiceField(
        queryset=models.AgeDivision.objects.all())
    weight_classes = ModelMultipleChoiceField(
        queryset=models.WeightClass.objects.all())

    class Meta:
        model = models.Board
        fields = []

    def save(self, commit: 'bool' = ...) -> 'List[models.Board]':
        definitions: 'QuerySet[models.BoardDefinition]' = self.cleaned_data['board_definitions']
        divisions: 'QuerySet[models.AgeDivision]' = self.cleaned_data['divisions']
        weight_classes: 'QuerySet[models.WeightClass]' = self.cleaned_data['weight_classes']

        def gen_boards():
            combos = product(definitions, divisions, weight_classes)
            for definition, division, weight_class in combos:
                board = models.Board()
                board.board_definition = definition
                board.division = division
                board.weight_class = weight_class
                yield board

        return models.Board.objects.bulk_create(gen_boards(), ignore_conflicts=True)


@admin.register(models.Board)
class BoardAdmin(CustomActionFormMixin, admin.ModelAdmin):
    custom_pages: 'Sequence[CustomAdminPage]' = [
        {
            'name': 'add-many',
            'form_class': AddManyBoardsForm,
            'help_text': '''For convenience, this page allows you to add many boards at once.
Here, you are able to select any combination of board definitions/weight classes, and divisions.
Then, we will permiate all the possible combinations of those selected fields. For example, if
you select 2 board definitions, 1 weight class, and 2 divisions, 2x2x1=4 boards will be created.'''
        }
    ]

    def get_page_context(self, options: 'CustomAdminPage') -> 'Dict[str, Any]':
        # render_change_form will set opts in the super call, but we need it now
        opts: 'Options' = self.model._meta
        context = super().get_page_context(options)
        context.update({
            'title': f'Add Many {opts.verbose_name_plural}',
            'has_multiselect': True,
        })
        return context

    def save_custom_form(self, request: 'HttpRequest', form: 'ModelForm'):
        created = super().save_custom_form(request, form)
        if isinstance(form, AddManyBoardsForm):
            assert isinstance(created, list)
            model_name = self.opts.verbose_name_plural if created != 1 else self.opts.verbose_name
            self.message_user(
                request, f'{len(created)} new {model_name} created')


@admin.register(models.WeightClass)
class WeightClassAdmin(admin.ModelAdmin):
    pass


def approve_score(_1: 'ScoreAdmin', _2: 'HttpRequest',
                  queryset: 'QuerySet[models.Score]'):
    queryset.update(approved=True)


approve_score.short_description = 'Approve selected scores'


@admin.register(models.Score)
class ScoreAdmin(AdminChangeLinksMixin, admin.ModelAdmin):
    actions = [approve_score]

    list_display = ['value', 'user_link',
                    'board__board_definition_link', 'board__division_link',
                    'board__weight_class_link', 'approved']
    change_links = ['user', 'board__board_definition',
                    'board__division', 'board__weight_class']

    list_filter = (
        ('board__board_definition', admin.RelatedOnlyFieldListFilter),
        ('board__division', admin.RelatedOnlyFieldListFilter),
        ('board__weight_class', admin.RelatedOnlyFieldListFilter),
        ('user', admin.RelatedOnlyFieldListFilter),
        'approved'
    )

    def changelist_view(self, request: 'HttpRequest',
                        extra_context: 'Optional[Dict[str, Any]]' = None) -> 'TemplateResponse':
        ctx: 'Dict[str, Any]' = extra_context or {}
        ctx.update({'has_multiselect': True})
        return super().changelist_view(request, extra_context=ctx)
