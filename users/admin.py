from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'validated_by_admin', 'is_active')
    list_filter = ('role', 'validated_by_admin', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'validated_by_admin', 'image')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
