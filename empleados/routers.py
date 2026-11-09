from rest_framework.routers import DefaultRouter

from .views import (
    RolViewSet,
    EmpleadoViewSet,
    EmpleadoListViewSet,
    EmpleadoRolViewSet,
    HorarioEmpleadoViewSet,
    AsistenciaEmpleadoViewSet,
)

router = DefaultRouter()
router.register('rol', RolViewSet, basename='rol-api')
router.register('empleado', EmpleadoViewSet, basename='empleado-api')
router.register('empleado-get', EmpleadoListViewSet, basename='empleado-get-api')
router.register('empleado-rol', EmpleadoRolViewSet, basename='empleado-rol-api')
router.register('horario', HorarioEmpleadoViewSet, basename='horario-api')
router.register('asistencia', AsistenciaEmpleadoViewSet, basename='asistencia-api')