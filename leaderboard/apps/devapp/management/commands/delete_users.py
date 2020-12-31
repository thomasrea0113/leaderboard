from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
User = get_user_model()

if TYPE_CHECKING:
    from typing import Any, Optional


class Command(BaseCommand):
    def handle(self, *args: 'Any', **options: 'Any') -> 'Optional[str]':
        return str(User.objects.all().delete())
