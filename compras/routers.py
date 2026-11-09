from rest_framework.routers import DefaultRouter

from .views import (
    ProveedorViewSet,
    TipoGastoViewSet,
    CompraViewSet,
    CompraListViewSet,
    DetalleCompraViewSet,
    GastoViewSet,
)

router = DefaultRouter()
router.register('proveedor', ProveedorViewSet, basename='proveedor-api')
router.register('tipo-gasto', TipoGastoViewSet, basename='tipo-gasto-api')
router.register('compra', CompraViewSet, basename='compra-api')
router.register('compra-get', CompraListViewSet, basename='compra-get-api')
router.register('detalle', DetalleCompraViewSet, basename='detalle-api')
router.register('gasto', GastoViewSet, basename='gasto-api')