from rest_framework.routers import DefaultRouter

from .views import (
    PlanTratamientoViewSet,
    PlanTratamientoListViewSet,
    ObjetivoTratamientoViewSet,
    ActividadPlanViewSet,
    HistorialMedicoViewSet,
    EvolucionSemanalViewSet,
    RegistroActividadViewSet,
    NotaImportanteViewSet,
)

router = DefaultRouter()
router.register('plan-tratamiento', PlanTratamientoViewSet, basename='plan-tratamiento-api')
router.register('plan-tratamiento-get', PlanTratamientoListViewSet, basename='plan-tratamiento-get-api')
router.register('objetivo', ObjetivoTratamientoViewSet, basename='objetivo-api')
router.register('actividad', ActividadPlanViewSet, basename='actividad-api')
router.register('historial-medico', HistorialMedicoViewSet, basename='historial-medico-api')
router.register('evolucion', EvolucionSemanalViewSet, basename='evolucion-api')
router.register('registro-actividad', RegistroActividadViewSet, basename='registro-actividad-api')
router.register('nota-importante', NotaImportanteViewSet, basename='nota-importante-api')