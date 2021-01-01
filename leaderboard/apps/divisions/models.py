from typing import TYPE_CHECKING
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import UniqueConstraint
from django.db.models.expressions import F
from django.db.models.query_utils import Q
from django.utils.translation import gettext as _

from apps.users.models import Genders

User = get_user_model()

if TYPE_CHECKING:
    from typing import Any


class WeightClass(models.Model):
    gender = models.CharField(
        max_length=1, blank=True, choices=Genders.choices, default=Genders.UNSPECIFIED)
    lower_bound = models.PositiveIntegerField(default=0)
    upper_bound = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        gender_str = f'{str(Genders(self.gender).label)}, '
        # TODO dynamically convert to lbs if the user prefers LBs
        return _(f'{gender_str}{self.lower_bound} - {self.upper_bound} KGs')

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(lower_bound__lt=F('upper_bound')) | Q(upper_bound=0),
                name='weight_range'),
            models.UniqueConstraint(
                fields=['lower_bound', 'upper_bound', 'gender'],
                name='unique_weight_class')
        ]


class AgeDivision(models.Model):
    name = models.CharField(max_length=50, unique=True)
    lower_bound = models.PositiveIntegerField(default=0)
    upper_bound = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return _(f'{self.name}, Ages {self.lower_bound} - {self.upper_bound}')

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(lower_bound__lt=F('upper_bound')) | Q(upper_bound=0),
                name='age_range'),
            models.UniqueConstraint(
                fields=['lower_bound', 'upper_bound'], name='unique_age_range')
        ]


class UnitType(models.TextChoices):
    DISTANCE = 'D', _('Distance')  # stored as meters
    POINTS = 'P', _('Points')
    TIME = 'T', _('Time')  # stored as seconds
    WEIGHT = 'W', _('Weight')  # stores as kilograms


class BoardDefinition(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unit_type = models.CharField(max_length=1, choices=UnitType.choices)
    description = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class Board(models.Model):
    board_definition = models.ForeignKey(
        BoardDefinition, on_delete=models.PROTECT)
    division = models.ForeignKey(
        AgeDivision, on_delete=models.PROTECT)
    weight_class = models.ForeignKey(
        WeightClass, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return (f'{self.board_definition.name} ({self.division}' +
                f', {self.weight_class})')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['board_definition', 'division', 'weight_class'], name="unique_board")
        ]


class Score(models.Model):
    id: 'Any'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=6, decimal_places=2)

    approved = models.BooleanField(blank=True, default=False)

    def __str__(self) -> str:
        return f'{self.value} {self.board.board_definition.unit_type}'

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(value__gt=0), name='value_gt0')
        ]
