from typing import TYPE_CHECKING
from django.contrib.auth.models import UserManager
from django.db import models
from django.db.models.expressions import ExpressionWrapper, F, RawSQL

UserManagerBase = UserManager

# can't directly import AppUser at runtime due to a circular reference
if TYPE_CHECKING:
    from .models import AppUser
    UserManagerBase = UserManager[AppUser]


class AppUserManager(UserManagerBase):
    def get_queryset(self):
        column = self.model._meta.get_field('birthday').column
        qry = super().get_queryset().extra(
            select={'age': "date_part('year', age(current_date, birthday))::int"})
        # qry = super().get_queryset().extra(select={
        #     'age': f"select DATE_PART('year', AGE(current_date, {column})))::int"})
        return qry
