from typing import TYPE_CHECKING
from itertools import product
from django.forms import ModelForm, ModelMultipleChoiceField
from .. import models

if TYPE_CHECKING:
    from typing import List
    from django.db.models.query import QuerySet


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
