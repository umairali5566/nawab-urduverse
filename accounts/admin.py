"""
Accounts Admin Configuration for Nawab Urdu Academy
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserActivity


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username', 'email', 'display_name', 'is_author', 
        'is_verified', 'is_active', 'date_joined'
    ]
    list_filter = ['is_author', 'is_verified', 'is_active', 'gender', 'date_joined']
    search_fields = ['username', 'email', 'display_name', 'first_name', 'last_name']
    list_editable = ['is_author', 'is_verified', 'is_active']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('اضافی معلومات', {
            'fields': (
                'display_name', 'bio', 'avatar', 'phone', 'gender',
                'birth_date', 'city', 'country', 'website',
                'facebook', 'twitter', 'instagram',
                'is_author', 'is_verified', 'dark_mode', 'email_notifications'
            )
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('اضافی معلومات', {
            'fields': ('display_name', 'email')
        }),
    )


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'description', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__username', 'description']
    readonly_fields = ['created_at']
