# apps/users/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import User


class IsAdmin(BasePermission):
    """Только Администратор"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsOperator(BasePermission):
    """Оператор + Администратор"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_operator


class IsOwnerOrReadOnly(BasePermission):
    """Владелец может редактировать, остальные — только читать"""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_admin or getattr(obj, 'user', None) == request.user


class IsOwner(BasePermission):
    """Только владелец объекта"""
    def has_object_permission(self, request, view, obj):
        return request.user.is_admin or getattr(obj, 'user', None) == request.user