from typing import cast, TYPE_CHECKING

from django.contrib.auth.base_user import AbstractBaseUser
from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import UserManager
from django.db.utils import IntegrityError

User = get_user_model()

if TYPE_CHECKING:
    from typing import Any, Optional


class Command(BaseCommand):
    def handle(self, *args: 'Any', **options: 'Any') -> 'Optional[str]':
        manager = cast(UserManager[AbstractBaseUser], User.objects)

        try:
            manager.create_superuser(
                username='thomasrea0113', email=None, password='Password123')
        except IntegrityError:
            pass

        try:
            manager.create_superuser(
                username='admin', email=None, password='Password123')
        except IntegrityError:
            pass
