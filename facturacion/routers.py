from rest_framework.routers import DefaultRouter

from .views import (
    FacturaVentaViewSet,
    FacturaVentaListViewSet,
    DetalleVentaViewSet,
    PagoViewSet,
)

router = DefaultRouter()
router.register('factura', FacturaVentaViewSet, basename='factura-api')
router.register('factura-get', FacturaVentaListViewSet, basename='factura-get-api')
router.register('detalle', DetalleVentaViewSet, basename='detalle-api')
router.register('pago', PagoViewSet, basename='pago-api')