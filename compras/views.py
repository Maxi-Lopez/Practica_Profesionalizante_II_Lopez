from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Proveedor, Compra, DetalleCompra, TipoGasto, Gasto
from .serializers import (
    ProveedorSerializer,
    ProveedorGetSerializer,
    DetalleCompraSerializer,
    DetalleCompraGetSerializer,
    CompraSerializer,
    CompraGetSerializer,
    TipoGastoSerializer,
    TipoGastoGetSerializer,
    GastoSerializer,
    GastoGetSerializer,
)
from core.permissions import EsAdminProfesionalRecepcionista


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-fecha_creacion']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [EsAdminProfesionalRecepcionista()]

    @action(detail=True, methods=['post'])
    def eliminado_logico(self, request, pk=None):
        obj = self.get_object()
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        obj.activo = False
        if hasattr(obj, 'razon_social'):
            obj.razon_social = f'delete-{obj.razon_social}-{timestamp}'
        elif hasattr(obj, 'nombre'):
            obj.nombre = f'delete-{obj.nombre}-{timestamp}'
        elif hasattr(obj, 'cuit'):
            obj.cuit = f'delete-{obj.cuit}-{timestamp}'
        obj.save()
        return Response({'detail': 'Eliminado correctamente'}, status=status.HTTP_200_OK)


class ProveedorViewSet(BaseViewSet):
    queryset = Proveedor.objects.filter(activo=True).order_by('razon_social')
    serializer_class = ProveedorSerializer
    search_fields = ['razon_social', 'cuit', 'email']
    filterset_fields = ['activo']
    ordering_fields = ['razon_social', 'fecha_creacion']


class ProveedorGetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Proveedor.objects.filter(activo=True).order_by('razon_social')
    serializer_class = ProveedorGetSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['razon_social', 'cuit', 'email']
    filterset_fields = ['activo']
    ordering_fields = ['razon_social', 'fecha_creacion']
    ordering = ['razon_social']


class CompraViewSet(BaseViewSet):
    queryset = Compra.objects.filter(anulada=False).select_related('proveedor').prefetch_related('detalles__producto').order_by('-fecha')
    serializer_class = CompraSerializer
    search_fields = ['numero_comprobante', 'proveedor__razon_social', 'observaciones']
    filterset_fields = ['proveedor', 'anulada', 'fecha']
    ordering_fields = ['fecha', 'numero_comprobante', 'total']

    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        obj = self.get_object()
        obj.anulada = True
        obj.save()
        return Response({'detail': 'Compra anulada correctamente'}, status=status.HTTP_200_OK)


class CompraGetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Compra.objects.filter(anulada=False).select_related('proveedor').prefetch_related('detalles__producto').order_by('-fecha')
    serializer_class = CompraGetSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['numero_comprobante', 'proveedor__razon_social', 'observaciones']
    filterset_fields = ['proveedor', 'anulada', 'fecha']
    ordering_fields = ['fecha', 'numero_comprobante', 'total']
    ordering = ['-fecha']


class DetalleCompraViewSet(BaseViewSet):
    queryset = DetalleCompra.objects.select_related('compra__proveedor', 'producto').order_by('-compra__fecha')
    serializer_class = DetalleCompraSerializer
    search_fields = ['producto__nombre', 'compra__numero_comprobante']
    filterset_fields = ['compra', 'producto']
    ordering_fields = ['compra__fecha', 'cantidad', 'subtotal']


class DetalleCompraGetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DetalleCompra.objects.select_related('compra__proveedor', 'producto').order_by('-compra__fecha')
    serializer_class = DetalleCompraGetSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['producto__nombre', 'compra__numero_comprobante']
    filterset_fields = ['compra', 'producto']
    ordering_fields = ['compra__fecha', 'cantidad', 'subtotal']
    ordering = ['-compra__fecha']


class TipoGastoViewSet(BaseViewSet):
    queryset = TipoGasto.objects.filter(activo=True).order_by('nombre')
    serializer_class = TipoGastoSerializer
    search_fields = ['nombre', 'descripcion']
    filterset_fields = ['activo']
    ordering_fields = ['nombre']


class TipoGastoGetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TipoGasto.objects.filter(activo=True).order_by('nombre')
    serializer_class = TipoGastoGetSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    filterset_fields = ['activo']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class GastoViewSet(BaseViewSet):
    queryset = Gasto.objects.filter(anulado=False).select_related('tipo_gasto', 'proveedor').order_by('-fecha')
    serializer_class = GastoSerializer
    search_fields = ['concepto', 'numero_comprobante', 'proveedor__razon_social', 'tipo_gasto__nombre']
    filterset_fields = ['tipo_gasto', 'proveedor', 'anulado', 'fecha']
    ordering_fields = ['fecha', 'monto', 'concepto']

    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        obj = self.get_object()
        obj.anulado = True
        obj.save()
        return Response({'detail': 'Gasto anulado correctamente'}, status=status.HTTP_200_OK)


class GastoGetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Gasto.objects.filter(anulado=False).select_related('tipo_gasto', 'proveedor').order_by('-fecha')
    serializer_class = GastoGetSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['concepto', 'numero_comprobante', 'proveedor__razon_social', 'tipo_gasto__nombre']
    filterset_fields = ['tipo_gasto', 'proveedor', 'anulado', 'fecha']
    ordering_fields = ['fecha', 'monto', 'concepto']
    ordering = ['-fecha']