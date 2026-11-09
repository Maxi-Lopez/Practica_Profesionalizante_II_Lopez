from rest_framework.routers import DefaultRouter

from .views import DocumentoViewSet, DocumentoListViewSet

router = DefaultRouter()
router.register('documento', DocumentoViewSet, basename='documento-api')
router.register('documento-get', DocumentoListViewSet, basename='documento-get-api')