from django.db import models
from django.utils.translation import gettext_lazy as _

# included as apposed ot in models.py to prevent circular references


class Genders(models.TextChoices):
    UNSPECIFIED = '', _('Unspecified')
    MALE = 'M', _('Male')
    FEMALE = 'F', _('Female')
