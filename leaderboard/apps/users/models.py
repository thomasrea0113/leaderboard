from typing import TYPE_CHECKING
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.query_utils import Q
from django.utils.translation import gettext_lazy as _

from apps.users.managers import AppUserManager

if TYPE_CHECKING:
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

    def get_eligable_weight_classes(self) -> 'QuerySet[WeightClass]':
        # all users are eligble of no weight bounds are specified
        weight_query = Q(lower_bound__lt=1, upper_bound__lt=1)
        if self.weight is not None:
            # both bounds. need separate queries because of repeated keys
            weight_query |= (Q(lower_bound__gt=0, upper_bound__gt=0) & Q(
                lower_bound__lte=self.weight, upper_bound__gt=self.weight))

            # no lower bound. need separate queries because of repeated keys
            weight_query |= (Q(lower_bound__lt=1, upper_bound__gt=0)
                             & Q(upper_bound__gt=self.weight))

            # no upper bound
            weight_query |= Q(
                lower_bound__gt=0, upper_bound__lt=1,
                lower_bound__lte=self.weight
            )

        # all users are eligble if no gender is specified
        gender_query = Q(gender=Genders.UNSPECIFIED)
        if self.gender != Genders.UNSPECIFIED:
            gender_query |= Q(gender=self.gender)

        # TODO Genders being in the user models module is causing a circular reference.
        # move genders to separate module caused the appUser module to appear as not registered
        # pylint: disable=import-outside-toplevel
        from apps.divisions.models import WeightClass

        # we then only want the intersection of both queries
        return WeightClass.objects.filter(weight_query & gender_query)
