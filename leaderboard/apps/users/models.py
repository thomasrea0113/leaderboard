from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import AbstractUser

from apps.users.managers import AppUserManager


class Genders(models.TextChoices):
    MALE = 'M', _('Male')
    FEMALE = 'F', _('Female')


# Create your models here.
class AppUser(AbstractUser):
    gender = models.CharField(max_length=6, choices=Genders.choices)
    birthday = models.DateField(blank=True, null=True)
    weight = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True)

    objects = AppUserManager()
