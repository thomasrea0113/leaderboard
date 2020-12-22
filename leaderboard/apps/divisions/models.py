from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.expressions import F
from django.db.models.query_utils import Q
from django.utils.translation import gettext_lazy as _

from apps.users.models import Genders

User = get_user_model()


class WeightClass(models.Model):
    gender = models.CharField(
        max_length=1, blank=True, choices=Genders.choices)
    lower_bound = models.PositiveIntegerField(default=0)
    upper_bound = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return (f'{self.lower_bound} - {self.upper_bound}' +
                (f' ({Genders(self.gender).label})' if self.gender else ''))

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(lower_bound__lt=F('upper_bound')) | Q(upper_bound=0),
                name='weight_range'),
            models.UniqueConstraint(
                fields=['lower_bound', 'upper_bound', 'gender'],
                name='unique_weight_range')
        ]


class AgeDivision(models.Model):
    name = models.CharField(max_length=50, unique=True)
    lower_bound = models.PositiveIntegerField(default=0)
    upper_bound = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f'{self.name} ({self.lower_bound} - {self.upper_bound})'

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
    name = models.CharField(max_length=100, null=True, unique=True)
    board_definition = models.ForeignKey(
        BoardDefinition, on_delete=models.PROTECT)
    division = models.ForeignKey(
        AgeDivision, on_delete=models.CASCADE, null=True, blank=True)
    weight_class = models.ForeignKey(
        WeightClass, on_delete=models.CASCADE, null=True, blank=True)


class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self) -> str:
        return f'{self.value} {self.board.unit_type}'

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(value__gt=0), name='value_gt0')
        ]
