# boards/permissions.py

from rest_framework import permissions

class IsBusinessAdmin(permissions.BasePermission):
    """
    사용자가 비즈니스 관리자(admin)인지 확인하는 퍼미션 클래스
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsOwnerOrBusinessAdmin(permissions.BasePermission):
    """
    객체의 소유자이거나 비즈니스 관리자만 접근할 수 있는 퍼미션 클래스
    """

    def has_object_permission(self, request, view, obj):
        return request.user.role == 'admin' or obj.author == request.user
