from typing import TYPE_CHECKING
from django.contrib.auth.models import UserManager
from django.db.models.expressions import RawSQL

UserManagerBase = UserManager

# can't directly import AppUser at runtime due to a circular reference
if TYPE_CHECKING:
    from .models import AppUser
    UserManagerBase = UserManager[AppUser]


class AppUserManager(UserManagerBase):
    def get_queryset(self):
        return super().get_queryset().annotate(age=RawSQL(
            "date_part('year', age(current_date, birthday))::int", []))
