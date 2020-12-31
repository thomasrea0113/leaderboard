
from typing import TYPE_CHECKING
from django.contrib import admin
from django.template.loader import render_to_string
from django.contrib.auth.admin import UserAdmin
from .models import AppUser

if TYPE_CHECKING:
    from typing import Optional
    from django.http import HttpRequest
    from django.db.models.options import Options


@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name',
                    'last_name', 'gender', 'is_staff', 'birthday', 'weight']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups', 'gender']

    readonly_fields = ['eligable_weight_classes']

    def eligable_weight_classes(self, user: 'AppUser'):
        query_set = user.get_eligable_weight_classes()
        meta: 'Options' = query_set.model._meta
        url_name = f'{self.admin_site.name}:{meta.app_label}_{meta.model_name}_change'

        return render_to_string('admin/includes/model_link_list.html', context={
            'url_name': url_name, 'query_set': query_set,
            'admin_site': self.admin_site})

    def changelist_view(self, request, extra_context=None):
        (extra_context := extra_context or {}).update(has_multiselect=True)
        return super().changelist_view(request, extra_context=extra_context)


# fieldsets is static, so we need to add them only once, not per instance
# typing is incorrect in the current version of the django-stubs
AppUserAdmin.fieldsets += (
    ('Eligibility', {'fields': ('eligable_weight_classes',)}),
)  # type: ignore[reportGeneralTypeIssues]
info = next(
    filter(lambda fs: fs[0] == 'Personal info', AppUserAdmin.fieldsets))[1]
# type: ignore[reportGeneralTypeIssues]
info['fields'] += ('gender', 'birthday', 'weight')
