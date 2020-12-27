from apps.divisions.models import AgeDivision, BoardDefinition, WeightClass
from apps.divisions.admin import AddManyBoardsForm
from typing import cast, TYPE_CHECKING

from django.contrib.auth.base_user import AbstractBaseUser
from django.core.management import BaseCommand, call_command
from django.contrib.auth import get_user_model
from django.contrib.auth.models import UserManager
from django.db.utils import IntegrityError

User = get_user_model()

if TYPE_CHECKING:
    from typing import Any, Optional


class Command(BaseCommand):
    def handle(self, *args: 'Any', **options: 'Any') -> 'Optional[str]':
        manager = cast(UserManager[AbstractBaseUser], User.objects)

        call_command('loaddata', 'usapl')

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

        frm = AddManyBoardsForm({
            'board_definitions': BoardDefinition.objects.all(),
            'divisions': AgeDivision.objects.all(),
            'weight_classes': WeightClass.objects.all()
        })

        if frm.is_valid():
            frm.save()
        else:
            raise Exception(frm.errors)

        # TODO restriction board creation for teen/junior only weight classes
