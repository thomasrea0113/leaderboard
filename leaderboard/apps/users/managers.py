from typing import TYPE_CHECKING
from django.contrib.auth.models import UserManager

UserManagerBase = UserManager

# can't directly import AppUser at runtime due to a circular reference
if TYPE_CHECKING:
    from .models import AppUser
    UserManagerBase = UserManager[AppUser]


class AppUserManager(UserManagerBase):
    def get_queryset(self):
        return super().get_queryset().extra(
            select={'age': "date_part('year', age(current_date, birthday))::int"})
