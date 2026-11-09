from rest_framework.routers import DefaultRouter

from .views import (
    TipoServicioViewSet,
    ServicioViewSet,
    ServicioListViewSet,
    ProfesionalServicioViewSet,
    ServicioObraSocialViewSet,
)

router = DefaultRouter()
router.register('tipo-servicio', TipoServicioViewSet, basename='tipo-servicio-api')
router.register('servicio', ServicioViewSet, basename='servicio-api')
router.register('servicio-get', ServicioListViewSet, basename='servicio-get-api')
router.register('profesional-servicio', ProfesionalServicioViewSet, basename='profesional-servicio-api')
router.register('servicio-obra-social', ServicioObraSocialViewSet, basename='servicio-obra-social-api')