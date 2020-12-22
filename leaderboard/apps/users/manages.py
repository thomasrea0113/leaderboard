from django.contrib.auth.models import UserManager
from typing import TYPE_CHECKING

UserManagerBase = UserManager

# can't directly import AppUser at runtime due to a circular reference
if TYPE_CHECKING:
    from .models import AppUser
    UserManagerBase = UserManager[AppUser]


class AppUserManager(UserManagerBase):
    pass
