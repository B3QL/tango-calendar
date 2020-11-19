from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from api.models import APIUser


class UserAdmin(BaseUserAdmin):
    """Admin model for User class"""
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('company_id', 'timezone')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('company_id', 'timezone')}),
    )


admin.site.register(APIUser, UserAdmin)
