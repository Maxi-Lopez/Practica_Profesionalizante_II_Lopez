from rest_framework import permissions


class EsAdmin(permissions.BasePermission):
    """
    Permiso para usuarios con rol 'admin' o superusuarios.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.rol == 'admin'


class EsProfesional(permissions.BasePermission):
    """
    Permiso para usuarios con rol 'profesional' o 'admin' o superusuarios.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.rol in ['profesional', 'admin']


class EsRecepcionista(permissions.BasePermission):
    """
    Permiso para usuarios con rol 'recepcionista' o 'admin' o superusuarios.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.rol in ['recepcionista', 'admin']


class EsAdminOProfesional(permissions.BasePermission):
    """
    Permiso para usuarios con rol 'admin' o 'profesional' o superusuarios.
    Usado para escritura en catálogos geográficos y personas.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.rol in ['admin', 'profesional']