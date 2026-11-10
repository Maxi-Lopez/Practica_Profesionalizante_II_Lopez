from rest_framework import permissions


class EsAdmin(permissions.BasePermission):
    """
    Permiso para usuarios con rol 'admin' o superusuarios.
    Acceso total al sistema.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.rol == 'admin'


class EsOrientador(permissions.BasePermission):
    """
    Permiso para usuarios con rol 'orientador' o superusuarios.
    Los orientadores pueden ver todo (diagnósticos y seguimientos de todas las áreas).
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.rol == 'orientador'


class EsProfesional(permissions.BasePermission):
    """
    Permiso para usuarios con rol 'profesional' o 'admin' o 'orientador' o superusuarios.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.rol in ['profesional', 'admin', 'orientador']


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
    Permiso para usuarios con rol 'admin', 'profesional', 'orientador' o superusuarios.
    Usado para escritura en catálogos geográficos y personas.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.rol in ['admin', 'profesional', 'orientador']


class EsAdminProfesionalRecepcionista(permissions.BasePermission):
    """
    Permiso para usuarios con rol 'admin', 'profesional', 'orientador', 'recepcionista' o superusuarios.
    Usado para escritura en pacientes, turnos, etc.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.rol in ['admin', 'profesional', 'orientador', 'recepcionista']


class PuedeVerDiagnosticoArea(permissions.BasePermission):
    """
    Permiso para ver diagnósticos por área.
    - Admin y Orientador: ven todos los diagnósticos de todas las áreas.
    - Profesional: solo ve los diagnósticos de SU área (user.area == diagnostico.area).
    - Recepcionista y Paciente: no tienen acceso.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        # Admin y Orientador tienen acceso total
        if request.user.rol in ['admin', 'orientador']:
            return True
        # Profesional tiene acceso (el filtrado se hace en get_queryset)
        if request.user.rol == 'profesional':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        # Admin y Orientador ven todo
        if request.user.rol in ['admin', 'orientador']:
            return True
        # Profesional solo ve los de su área
        if request.user.rol == 'profesional':
            return obj.area == request.user.area
        return False


class PuedeVerSeguimientoTrimestral(permissions.BasePermission):
    """
    Permiso para ver seguimientos trimestrales por área.
    - Admin y Orientador: ven todos los seguimientos de todas las áreas.
    - Profesional: solo ve los seguimientos de SU área (user.area == seguimiento.area).
    - Recepcionista y Paciente: no tienen acceso.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        # Admin y Orientador tienen acceso total
        if request.user.rol in ['admin', 'orientador']:
            return True
        # Profesional tiene acceso (el filtrado se hace en get_queryset)
        if request.user.rol == 'profesional':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        # Admin y Orientador ven todo
        if request.user.rol in ['admin', 'orientador']:
            return True
        # Profesional solo ve los de su área
        if request.user.rol == 'profesional':
            return obj.area == request.user.area
        return False