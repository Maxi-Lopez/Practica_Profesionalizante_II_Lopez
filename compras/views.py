from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction

from .models import Proveedor, Compra, DetalleCompra, TipoGasto, Gasto
from .serializers import (
    ProveedorSerializer,
    TipoGastoSerializer,
    CompraSerializer,
    CompraListSerializer,
    DetalleCompraSerializer,
    DetalleCompraListSerializer,
    GastoSerializer,
    GastoListSerializer,
)
from personas.permissions import EsAdmin


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-fecha_creacion']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [EsAdmin()]

    @action(detail=True, methods=['post'])
    def eliminado_logico(self, request, pk=None):
        obj = self.get_object()
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        obj.activo = False
        if hasattr(obj, 'razon_social'):
            obj.razon_social = f'delete-{obj.razon_social}-{timestamp}'
        elif hasattr(obj, 'nombre'):
            obj.nombre = f'delete-{obj.nombre}-{timestamp}'
        elif hasattr(obj, 'cuit') and obj.cuit:
            obj.cuit = f'delete-{obj.cuit}-{timestamp}'
        obj.save()
        return Response({'detail': 'Eliminado correctamente'}, status=status.HTTP_200_OK)


class ProveedorViewSet(BaseViewSet):
    queryset = Proveedor.objects.filter(activo=True).order_by('razon_social')
    serializer_class = ProveedorSerializer
    search_fields = ['razon_social', 'cuit', 'email']
    filterset_fields = ['activo']
    ordering_fields = ['razon_social', 'fecha_creacion']


class TipoGastoViewSet(BaseViewSet):
    queryset = TipoGasto.objects.filter(activo=True).order_by('nombre')
    serializer_class = TipoGastoSerializer
    search_fields = ['nombre', 'descripcion']
    filterset_fields = ['activo']
    ordering_fields = ['nombre']


class CompraViewSet(BaseViewSet):
    queryset = Compra.objects.select_related('proveedor').prefetch_related('detalles__producto', 'gastos__tipo_gasto', 'gastos__proveedor').order_by('-fecha')
    serializer_class = CompraSerializer
    search_fields = ['numero_comprobante', 'proveedor__razon_social', 'observaciones']
    filterset_fields = ['proveedor', 'anulada']
    ordering_fields = ['fecha', 'total', 'numero_comprobante']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CompraListSerializer
        return CompraSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        compra = serializer.save()
        return Response(CompraListSerializer(compra).data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        compra = serializer.save()
        return Response(CompraListSerializer(compra).data)

    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        compra = self.get_object()
        compra.anulada = True
        compra.save()
        return Response({'detail': 'Compra anulada correctamente'}, status=status.HTTP_200_OK)


class CompraListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Compra.objects.select_related('proveedor').prefetch_related('detalles__producto', 'gastos__tipo_gasto', 'gastos__proveedor').order_by('-fecha')
    serializer_class = CompraListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['numero_comprobante', 'proveedor__razon_social', 'observaciones']
    filterset_fields = ['proveedor', 'anulada']
    ordering_fields = ['fecha', 'total', 'numero_comprobante']
    ordering = ['-fecha']


class DetalleCompraViewSet(BaseViewSet):
    queryset = DetalleCompra.objects.select_related('compra__proveedor', 'producto__categoria').order_by('-compra__fecha')
    serializer_class = DetalleCompraSerializer
    search_fields = ['compra__numero_comprobante', 'producto__nombre', 'producto__codigo']
    filterset_fields = ['compra', 'producto']
    ordering_fields = ['cantidad', 'precio_unitario', 'subtotal']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return DetalleCompraListSerializer
        return DetalleCompraSerializer


class GastoViewSet(BaseViewSet):
    queryset = Gasto.objects.select_related('tipo_gasto', 'proveedor').order_by('-fecha')
    serializer_class = GastoSerializer
    search_fields = ['concepto', 'numero_comprobante', 'tipo_gasto__nombre', 'proveedor__razon_social']
    filterset_fields = ['tipo_gasto', 'proveedor', 'anulado']
    ordering_fields = ['fecha', 'monto']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GastoListSerializer
        return GastoSerializer