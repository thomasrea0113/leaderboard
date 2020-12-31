from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.query_utils import Q
from django.utils.translation import gettext_lazy as _

from apps.users.managers import AppUserManager


class Genders(models.TextChoices):
    MALE = 'M', _('Male')
    FEMALE = 'F', _('Female')


# Create your models here.
class AppUser(AbstractUser):
    gender = models.CharField(max_length=6, choices=Genders.choices)
    birthday = models.DateField(blank=True, null=True)
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)

    objects = AppUserManager()

    def get_eligable_weight_classes(self):
        # TODO Genders being in the user models module is causing a circular reference.
        # move genders to separate module caused the appUser module to appear as not registered
        # pylint: disable=import-outside-toplevel
        from apps.divisions.models import WeightClass

        filtered = WeightClass.objects.get_queryset()

        # TODO finish filtering
        if self.weight is not None:
            # for weight classes with both bounds
            filtered = filtered.filter(
                Q(lower_bound__gt=0, upper_bound__gt=0) &
                Q(lower_bound__lte=self.weight, upper_bound__gt=self.weight))
        else:
            # user has no weight, only eligble for weight classes with no bounds specified
            filtered = filtered.filter(lower_bound__eq=0, upper_bound__eq=0)

        return filtered
