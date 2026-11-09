from rest_framework.routers import DefaultRouter

from .views import (
    CategoriaProductoViewSet,
    ProductoViewSet,
    ProductoListViewSet,
    MovimientoStockViewSet,
    MovimientoStockListViewSet,
)

router = DefaultRouter()
router.register('categoria', CategoriaProductoViewSet, basename='categoria-api')
router.register('producto', ProductoViewSet, basename='producto-api')
router.register('producto-get', ProductoListViewSet, basename='producto-get-api')
router.register('movimiento', MovimientoStockViewSet, basename='movimiento-api')
router.register('movimiento-get', MovimientoStockListViewSet, basename='movimiento-get-api')