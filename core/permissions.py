"""
Role-based access control utilities for Nawab Urdu Academy
"""

from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


def admin_only(view_func):
    """
    Decorator to restrict view access to superusers/admins only.
    Regular users will see a forbidden message.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_required(view_func)(request, *args, **kwargs)
        
        if not request.user.is_superuser:
            return HttpResponseForbidden(
                "<h1>Access Denied</h1><p>Only administrators can access this resource.</p>"
            )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def superuser_required(view_func):
    """
    Alternative name for admin_only decorator.
    Requires user to be logged in and have superuser status.
    """
    return admin_only(view_func)


class AdminOnlyMixin:
    """
    Mixin for class-based views to restrict access to superusers only.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        
        if not request.user.is_superuser:
            return HttpResponseForbidden(
                "<h1>Access Denied</h1><p>Only administrators can access this resource.</p>"
            )
        
        return super().dispatch(request, *args, **kwargs)


def user_is_admin(user):
    """
    Helper function to check if user is admin/superuser.
    Use in templates with {% if user_is_admin %} after passing it to context.
    """
    return user.is_authenticated and user.is_superuser
