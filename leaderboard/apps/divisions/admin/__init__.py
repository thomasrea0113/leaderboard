from typing import TYPE_CHECKING

from django.urls.resolvers import get_resolver
from django.contrib import admin
from django.forms import ModelForm

from apps.divisions.admin.actions import approve_score
from apps.home.mixins.admin import AdminChangeLinksMixin, \
    AdminSelect2ListFilterMixin, CustomActionFormMixin

from . import forms
from .. import models


resolve = get_resolver().resolve

if TYPE_CHECKING:
    from typing import Any, Dict, Sequence
    from django.db.models.options import Options
    from django.http import HttpRequest
    from apps.home.mixins.admin import CustomAdminPage


@admin.register(models.AgeDivision)
class AgeDivisionAdmin(AdminSelect2ListFilterMixin, admin.ModelAdmin):
    list_display = ('name', 'lower_bound', 'upper_bound')
    list_filter = ('lower_bound', 'upper_bound')


@admin.register(models.BoardDefinition)
class BoardDefinitionAdmin(AdminSelect2ListFilterMixin, admin.ModelAdmin):
    list_display = ('name', 'unit_type', 'description')
    list_filter = ('unit_type',)


@admin.register(models.Board)
class BoardAdmin(AdminSelect2ListFilterMixin, AdminChangeLinksMixin,
                 CustomActionFormMixin, admin.ModelAdmin):
    list_display = ('__str__', 'board_definition_link',
                    'weight_class_link', 'division_link')
    change_links = ('board_definition', 'division', 'weight_class')
    list_filter = (
        ('board_definition', admin.RelatedOnlyFieldListFilter),
        ('division', admin.RelatedOnlyFieldListFilter),
        ('weight_class', admin.RelatedOnlyFieldListFilter)
    )
    custom_pages: 'Sequence[CustomAdminPage]' = [
        {
            'name': 'add-many',
            'form_class': forms.AddManyBoardsForm,
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

        if options['name'] == 'add-many':
            context.update({
                'title': f'Add Many {opts.verbose_name_plural}',
                'has_multiselect': True,
            })

        return context

    def save_custom_form(self, request: 'HttpRequest', form: 'ModelForm'):
        created = super().save_custom_form(request, form)
        if isinstance(form, forms.AddManyBoardsForm):
            assert isinstance(created, list)
            model_name = self.opts.verbose_name_plural if created != 1 else self.opts.verbose_name
            self.message_user(
                request, f'{len(created)} new {model_name} created')


@admin.register(models.WeightClass)
class WeightClassAdmin(AdminSelect2ListFilterMixin, admin.ModelAdmin):
    list_display = ['__str__', 'gender', 'lower_bound', 'upper_bound']
    list_filter = ['gender', 'lower_bound', 'upper_bound']


@admin.register(models.Score)
class ScoreAdmin(AdminSelect2ListFilterMixin, AdminChangeLinksMixin, admin.ModelAdmin):
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
