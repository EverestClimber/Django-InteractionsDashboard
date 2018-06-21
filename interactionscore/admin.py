from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.urls import resolve
from django.contrib.auth.models import Permission
import nested_admin
from safedelete.admin import SafeDeleteAdmin, highlight_deleted

from .models import (
    AffiliateGroup,
    TherapeuticArea,
    Comment,
    EngagementPlan,
    EngagementListItem,
    HCPObjective,
    HCPDeliverable,
    HCP,
    User,
)

admin.site.site_header = "Otsuka Interactions Admin"
admin.site.site_title = "Otsuka Interactions Admin"
admin.site.index_title = "Welcome to Otsuka Interactions Admin"


@admin.register(AffiliateGroup)
class AffiliateGroupAdmin(SafeDeleteAdmin):
    model = AffiliateGroup
    list_display = (highlight_deleted, "name") + SafeDeleteAdmin.list_display
    list_filter = SafeDeleteAdmin.list_filter


@admin.register(TherapeuticArea)
class TherapeuticAreaAdmin(SafeDeleteAdmin):
    model = TherapeuticArea
    list_display = (highlight_deleted, "name") + SafeDeleteAdmin.list_display
    list_filter = SafeDeleteAdmin.list_filter


@admin.register(Comment)
class CommentAdmin(SafeDeleteAdmin):
    model = Comment
    list_display = (highlight_deleted, "user") + SafeDeleteAdmin.list_display
    list_filter = ("user",) + SafeDeleteAdmin.list_filter


class CommentInline(nested_admin.NestedStackedInline):
    model = Comment
    fields = ('user', 'message')
    extra = 0


class EngagementListItemInline(nested_admin.NestedStackedInline):
    model = EngagementListItem
    fields = ('hcp', 'approved',)
    extra = 0
    inlines = (CommentInline,)


class HCPDeliverableInline(nested_admin.NestedTabularInline):
    model = HCPDeliverable
    fields = ('quarter', 'description')
    extra = 0


class HCPObjectiveInline(nested_admin.NestedStackedInline):
    model = HCPObjective
    fields = ('hcp', 'description', 'approved',)
    extra = 0
    inlines = (
        HCPDeliverableInline,
        CommentInline,
    )


def action_engagement_plans_approve(modeladmin, request, queryset):
    for eplan in queryset:
        eplan.approve()


action_engagement_plans_approve.short_description = 'Approve'


def action_engagement_plans_undo_approval(modeladmin, request, queryset):
    for eplan in queryset:
        eplan.unapprove()


action_engagement_plans_undo_approval.short_description = 'Undo Approval'


@admin.register(EngagementPlan)
class EngagementPlanAdmin(nested_admin.NestedModelAdmin, SafeDeleteAdmin):
    model = EngagementPlan
    list_display = (highlight_deleted, 'id', 'user', 'approved') + SafeDeleteAdmin.list_display
    fieldsets = (
        (None, {'fields': (
            'user',
            'year',
            'approved',
        )}),
        (_('Timestamps'), {
            'fields': (
                'created_at',
                'updated_at',
                'approved_at',
            ),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at', 'approved')
    actions = (action_engagement_plans_approve, action_engagement_plans_undo_approval)
    inlines = (
        EngagementListItemInline,
        HCPObjectiveInline,
    )
    list_filter = ("approved", "user", "year") + SafeDeleteAdmin.list_filter


@admin.register(HCP)
class HCPAdmin(SafeDeleteAdmin):
    model = HCP
    list_display = (
                       highlight_deleted,
                       "institution_name",
                       "hcp_affiliate_groups",
                   ) + SafeDeleteAdmin.list_display
    list_filter = SafeDeleteAdmin.list_filter

    def hcp_affiliate_groups(self, obj):
        return ", ".join([ag.name for ag in obj.affiliate_groups.all()])


@admin.register(User)
class UserAdmin(BaseUserAdmin, SafeDeleteAdmin):
    add_form_template = 'admin/auth/user/add_form.html'
    change_user_password_template = None
    fieldsets = (
        (None, {'fields': ('email', 'password', 'business_title')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Affiliate groups'), {'fields': ('affiliate_groups',)}),
        (_('Therapeutic Areas'), {'fields': ('tas',)}),
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
    list_display = (
                       'email', 'roles_and_groups', 'user_affiliate_groups',
                       'is_staff', 'is_superuser'
                   ) + SafeDeleteAdmin.list_display
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

    def roles_and_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])

    def user_affiliate_groups(self, obj):
        return ", ".join([ag.name for ag in obj.affiliate_groups.all()])


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    model = Permission
    list_display = ('desc', 'codename',)

    def desc(self, obj):
        return str(obj)
