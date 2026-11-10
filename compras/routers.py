from rest_framework.routers import DefaultRouter

from .views import (
    ProveedorViewSet,
    ProveedorGetViewSet,
    CompraViewSet,
    CompraGetViewSet,
    DetalleCompraViewSet,
    DetalleCompraGetViewSet,
    TipoGastoViewSet,
    TipoGastoGetViewSet,
    GastoViewSet,
    GastoGetViewSet,
)

router = DefaultRouter()
router.register('proveedor', ProveedorViewSet, basename='proveedor-api')
router.register('proveedor-get', ProveedorGetViewSet, basename='proveedor-get-api')
router.register('compra', CompraViewSet, basename='compra-api')
router.register('compra-get', CompraGetViewSet, basename='compra-get-api')
router.register('detalle', DetalleCompraViewSet, basename='detalle-api')
router.register('detalle-get', DetalleCompraGetViewSet, basename='detalle-get-api')
router.register('tipo-gasto', TipoGastoViewSet, basename='tipo-gasto-api')
router.register('tipo-gasto-get', TipoGastoGetViewSet, basename='tipo-gasto-get-api')
router.register('gasto', GastoViewSet, basename='gasto-api')
router.register('gasto-get', GastoGetViewSet, basename='gasto-get-api')