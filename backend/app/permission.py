from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    ''' Разрешение только для автора '''

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)


class IsAdminOrReadOnly(permissions.BasePermission):
    ''' Разрешение только для админа '''

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin or request.user.is_superuser)
