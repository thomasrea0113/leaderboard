from typing import TYPE_CHECKING

from django.urls.resolvers import get_resolver
from django.contrib import admin
from django.forms import ModelForm

from apps.divisions.admin.actions import approve_score
from apps.home.mixins.admin.admin import CustomActionFormMixin
from apps.home.mixins.admin import AdminChangeLinksMixin

from .. import models
from . import forms


resolve = get_resolver().resolve

if TYPE_CHECKING:
    from typing import Any, Optional, Dict, Sequence
    from django.db.models.options import Options
    from django.http import HttpRequest
    from django.template.response import TemplateResponse
    from apps.home.mixins.admin import CustomAdminPage


@admin.register(models.AgeDivision)
class AgeDivisionAdmin(admin.ModelAdmin):
    pass


@admin.register(models.BoardDefinition)
class BoardDefinitionAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Board)
class BoardAdmin(CustomActionFormMixin, admin.ModelAdmin):
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
class WeightClassAdmin(admin.ModelAdmin):
    pass


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
