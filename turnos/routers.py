from rest_framework.routers import DefaultRouter

from .views import (
    TurnoViewSet,
    TurnoListViewSet,
    AsistenciaPacienteViewSet,
)

router = DefaultRouter()
router.register('turno', TurnoViewSet, basename='turno-api')
router.register('turno-get', TurnoListViewSet, basename='turno-get-api')
router.register('asistencia', AsistenciaPacienteViewSet, basename='asistencia-api')