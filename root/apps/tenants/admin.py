from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Organization, OrganizationMembership, Plan

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'owner', 'plan', 'is_active')
    search_fields = ('name', 'slug', 'owner__email')

@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'is_active')
    search_fields = ('user__email', 'organization__name')

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_users')
