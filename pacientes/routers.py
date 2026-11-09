from rest_framework.routers import DefaultRouter

from .views import (
    ObraSocialViewSet,
    TipoDiagnosticoViewSet,
    DiagnosticoViewSet,
    PacienteViewSet,
    PacienteListViewSet,
    ResponsablePacienteViewSet,
    PacienteDiagnosticoViewSet,
)

router = DefaultRouter()
router.register('obra-social', ObraSocialViewSet, basename='obra-social-api')
router.register('tipo-diagnostico', TipoDiagnosticoViewSet, basename='tipo-diagnostico-api')
router.register('diagnostico', DiagnosticoViewSet, basename='diagnostico-api')
router.register('paciente', PacienteViewSet, basename='paciente-api')
router.register('paciente-get', PacienteListViewSet, basename='paciente-get-api')
router.register('responsable', ResponsablePacienteViewSet, basename='responsable-api')
router.register('paciente-diagnostico', PacienteDiagnosticoViewSet, basename='paciente-diagnostico-api')