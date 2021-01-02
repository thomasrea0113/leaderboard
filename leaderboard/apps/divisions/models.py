from abc import abstractmethod
from typing import TYPE_CHECKING
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import UniqueConstraint
from django.db.models.expressions import F
from django.db.models.query_utils import Q
from django.utils.translation import gettext as _

from apps.users.models import AppUser, Genders

User = get_user_model()

if TYPE_CHECKING:
    from typing import Any
    from django.db.models.query import QuerySet


class BoundModel(models.Model):
    lower_bound = models.PositiveIntegerField(default=0)
    upper_bound = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
        constraints = [
            models.CheckConstraint(
                check=Q(lower_bound__lt=F('upper_bound')) | Q(upper_bound=0),
                name='%(app_label)s_%(class)s_range')
        ]

    def __satisfied_users_query(self, user_field_name: 'str'):
        lower_bound = self.lower_bound
        upper_bound = self.upper_bound

        # all users are eligble if no bounds are specified
        if lower_bound == 0 and upper_bound == 0:
            return Q(pk__isnull=False)

        # both bounds set
        if lower_bound != 0 and upper_bound != 0:
            query = Q(**{
                f'{user_field_name}__gte': lower_bound,
                f'{user_field_name}__lt': upper_bound})

        # upper bound set
        elif upper_bound != 0:
            query = Q(**{f'{user_field_name}__lt': upper_bound})

        # lower bound set. Ff both are not zero, but upper bound is all not zero,
        # then lower bound must be zero
        else:
            query = Q(**{f'{user_field_name}__gt': lower_bound})

        # if the bounds are set, the user must have a value for the comparing field
        not_null = Q(**{f'{user_field_name}__isnull': False})

        return not_null & query

    def _get_eligble_users(self, user_field_name: 'str') -> 'QuerySet[AppUser]':
        """Gets a query that can be used to find users who's provided field
        fall within this models bounds
        """
        query = self.__satisfied_users_query(user_field_name)
        return User.objects.filter(query)

    @abstractmethod
    def get_eligble_users(self) -> 'QuerySet[AppUser]':
        raise NotImplementedError()


class WeightClass(BoundModel):
    gender = models.CharField(
        max_length=1, blank=True, choices=Genders.choices, default=Genders.UNSPECIFIED)

    def __str__(self) -> str:
        gender_str = f'{str(Genders(self.gender).label)}, '
        # TODO dynamically convert to lbs if the user prefers LBs
        return _(f'{gender_str}{self.lower_bound} - {self.upper_bound} KGs')

    class Meta:
        constraints = BoundModel.Meta.constraints + [
            models.UniqueConstraint(
                fields=['lower_bound', 'upper_bound', 'gender'],
                name='unique_weight_class')
        ]  # type: ignore[reportGeneralTypeIssues]

    def get_eligble_users(self) -> 'QuerySet[AppUser]':
        """Gets a query that can be used to find users who's provided field
        fall within this models bounds
        """
        eligble = super()._get_eligble_users('weight')

        if self.gender != Genders.UNSPECIFIED:
            eligble = eligble.filter(gender=self.gender)

        return eligble


class AgeDivision(BoundModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return _(f'{self.name}, Ages {self.lower_bound} - {self.upper_bound}')

    class Meta:
        constraints = BoundModel.Meta.constraints + [
            models.UniqueConstraint(
                fields=['lower_bound', 'upper_bound'], name='unique_age_range')
        ]  # type: ignore[reportGeneralTypeIssues]

    def get_eligble_users(self) -> 'QuerySet[AppUser]':
        return self._get_eligble_users('age')


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

    def get_eligble_users(self):
        # TODO implement
        weight_class: 'WeightClass' = self.weight_class
        division: 'AgeDivision' = self.division
        return weight_class.get_eligble_users().intersection(division.get_eligble_users())


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
