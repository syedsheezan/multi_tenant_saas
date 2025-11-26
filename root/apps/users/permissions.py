# apps/users/permissions.py
from rest_framework import permissions

class IsAdminOrSelf(permissions.BasePermission):
    """
    Object-level permission to only allow staff/superuser OR the user themself
    to access/modify the User object.

    Usage:
      - In class-based views that call has_object_permission, or
      - You can call perm.has_object_permission(request, view, obj) manually.
    """
    def has_permission(self, request, view):
        # default allow at view-level; object-level checks are enforced separately
        return True

    def has_object_permission(self, request, view, obj):
        # obj is an instance of your User model
        if not request.user or not request.user.is_authenticated:
            return False
        # staff or superuser can do anything
        if request.user.is_staff or request.user.is_superuser:
            return True
        # otherwise only the user themself may operate
        return obj.pk == request.user.pk
