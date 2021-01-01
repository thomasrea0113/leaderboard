from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.home.widgets.admin import ModelChangeListWidget

from .models import AppUser


@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name',
                    'last_name', 'gender', 'is_staff', 'birthday', 'weight']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups', 'gender']

    readonly_fields = ['age', 'eligable_weight_classes',
                       'eligable_age_divisions']

    def eligable_age_divisions(self, user: 'AppUser'):
        return ModelChangeListWidget(self.admin_site).render('eligble-age-divisions',
                                                             user.get_eligable_age_divisions())

    def eligable_weight_classes(self, user: 'AppUser'):
        return ModelChangeListWidget(self.admin_site).render('eligble-weight-classes',
                                                             user.get_eligable_weight_classes())

    def changelist_view(self, request, extra_context=None):
        (extra_context := extra_context or {}).update(has_multiselect=True)
        return super().changelist_view(request, extra_context=extra_context)


# fieldsets is static, so we need to add them only once, not per instance
# typing is incorrect in the current version of the django-stubs

AppUserAdmin.fieldsets += (('Eligibility',
                            {
                                'fields': ('eligable_weight_classes', 'eligable_age_divisions')
                            }),)  # type: ignore[reportGeneralTypeIssues]
info = next(
    filter(lambda fs: fs[0] == 'Personal info', AppUserAdmin.fieldsets))[1]
# type: ignore[reportGeneralTypeIssues]
info['fields'] += ('gender', 'birthday', 'age', 'weight')
