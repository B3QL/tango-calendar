from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from api.models import APIUser, Location, Meeting


class UserAdmin(BaseUserAdmin):
    """Admin model for User class"""
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('company_id', 'timezone')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('company_id', 'timezone')}),
    )


class LocationAdmin(admin.ModelAdmin):
    pass


class MeetingAdmin(admin.ModelAdmin):
    pass


admin.site.register(APIUser, UserAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Meeting, MeetingAdmin)
