from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.urls import resolve
import nested_admin

from .models import (
    AffiliateGroup,
    EngagementPlan,
    User,
)


admin.site.site_header = "Otsuka Interactions Admin"
admin.site.site_title = "Otsuka Interactions Admin"
admin.site.index_title = "Welcome to Otsuka Interactions Admin"


@admin.register(AffiliateGroup)
class AffiliateGroupAdmin(admin.ModelAdmin):
    model = AffiliateGroup


@admin.register(EngagementPlan)
class EngagementPlanAdmin(admin.ModelAdmin):
    model = EngagementPlan
    list_display = ('id', 'user', 'approved')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form_template = 'admin/auth/user/add_form.html'
    change_user_password_template = None
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Affiliate groups'), {'fields': ('affiliate_groups',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
