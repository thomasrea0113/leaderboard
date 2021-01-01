from datetime import date
from functools import lru_cache
from typing import TYPE_CHECKING
from dateutil.relativedelta import relativedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.query_utils import Q
from django.utils.translation import gettext_lazy as _

from apps.users.managers import AppUserManager

if TYPE_CHECKING:
    from typing import Any
    from django.db.models.query import QuerySet
    from apps.divisions.models import WeightClass


class Genders(models.TextChoices):
    UNSPECIFIED = '', _('Unspecified')
    MALE = 'M', _('Male')
    FEMALE = 'F', _('Female')


# Create your models here.
class AppUser(AbstractUser):
    gender = models.CharField(
        max_length=6, choices=Genders.choices, default=Genders.UNSPECIFIED, blank=True)
    birthday = models.DateField(blank=True, null=True)

    weight = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)

    objects = AppUserManager()

    @property
    def age(self):
        return relativedelta(date.today(), self.birthday).years if self.birthday else None

    # TODO investigate cache sizes
    @staticmethod
    @lru_cache(150)
    def __get_bound_query(value: 'Any'):
        # all users are eligble of no weight bounds are specified
        query = Q(lower_bound__lt=1, upper_bound__lt=1)
        if value is not None:
            # both bounds. need separate queries because of repeated keys
            query |= (Q(lower_bound__gt=0, upper_bound__gt=0) & Q(
                lower_bound__lte=value, upper_bound__gt=value))

            # no lower bound. need separate queries because of repeated keys
            query |= (Q(lower_bound__lt=1, upper_bound__gt=0)
                      & Q(upper_bound__gt=value))

            # no upper bound
            query |= Q(
                lower_bound__gt=0, upper_bound__lt=1,
                lower_bound__lte=value
            )

        return query

    def get_eligable_weight_classes(self) -> 'QuerySet[WeightClass]':
        bound_query = self.__get_bound_query(self.weight)

        # all users are eligble if no gender is specified
        gender_query = Q(gender=Genders.UNSPECIFIED)
        if self.gender != Genders.UNSPECIFIED:
            gender_query |= Q(gender=self.gender)

        # TODO Genders being in the user models module is causing a circular reference.
        # move genders to separate module caused the appUser module to appear as not registered
        # pylint: disable=import-outside-toplevel
        from apps.divisions.models import WeightClass

        # we then only want the intersection of both queries
        return WeightClass.objects.filter(bound_query & gender_query)

    def get_eligable_age_divisions(self) -> 'QuerySet[WeightClass]':
        query = self.__get_bound_query(self.age)

        # TODO Genders being in the user models module is causing a circular reference.
        # move genders to separate module caused the appUser module to appear as not registered
        # pylint: disable=import-outside-toplevel
        from apps.divisions.models import AgeDivision

        return AgeDivision.objects.filter(query)
