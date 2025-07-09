from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from . import models


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    model = models.User

    list_display = ('phone_number', 'email', 'is_active', 'last_login', 'role')
    list_filter = ('is_active', 'role', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': (
            'phone_number', 'email', 'password', 'role', 'national_id', 'first_name',
            'last_name',)}),
        ('Permissions',
         {'fields': ('is_active', 'is_phone_number_confirmed', 'is_national_id_confirmed')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'email', 'password1', 'password2', 'is_active',
                       'is_phone_number_confirmed', 'first_name', 'last_name', 'national_id',
                       'role')}
         ),
    )
    search_fields = ('phone_number',)
    ordering = ('phone_number',)
    filter_horizontal = ()


admin.site.register(models.User, CustomUserAdmin)
admin.site.register(models.UserBlock)
admin.site.register(models.UserProfileModel)
