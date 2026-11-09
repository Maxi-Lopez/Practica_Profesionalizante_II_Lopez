from rest_framework.routers import DefaultRouter

from .views import (
    PaisViewSet,
    ProvinciaViewSet,
    LocalidadViewSet,
    PersonaViewSet,
    PersonaListViewSet,
)

router = DefaultRouter()
router.register('pais', PaisViewSet, basename='pais-api')
router.register('provincia', ProvinciaViewSet, basename='provincia-api')
router.register('localidad', LocalidadViewSet, basename='localidad-api')
router.register('persona', PersonaViewSet, basename='persona-api')
router.register('persona-get', PersonaListViewSet, basename='persona-get-api')