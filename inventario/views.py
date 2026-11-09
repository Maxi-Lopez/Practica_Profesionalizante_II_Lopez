from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import CategoriaProducto, Producto, MovimientoStock
from .serializers import (
    CategoriaProductoSerializer,
    ProductoSerializer,
    ProductoListSerializer,
    MovimientoStockSerializer,
    MovimientoStockListSerializer,
)
from personas.permissions import EsAdmin


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-fecha_creacion']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        # Escritura solo para admin
        return [EsAdmin()]

    @action(detail=True, methods=['post'])
    def eliminado_logico(self, request, pk=None):
        obj = self.get_object()
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        obj.activo = False
        if hasattr(obj, 'nombre'):
            obj.nombre = f'delete-{obj.nombre}-{timestamp}'
        elif hasattr(obj, 'codigo') and obj.codigo:
            obj.codigo = f'delete-{obj.codigo}-{timestamp}'
        obj.save()
        return Response({'detail': 'Eliminado correctamente'}, status=status.HTTP_200_OK)


class CategoriaProductoViewSet(BaseViewSet):
    queryset = CategoriaProducto.objects.filter(activo=True).order_by('nombre')
    serializer_class = CategoriaProductoSerializer
    search_fields = ['nombre', 'descripcion']
    filterset_fields = ['activo']
    ordering_fields = ['nombre']


class ProductoViewSet(BaseViewSet):
    queryset = Producto.objects.filter(activo=True).select_related('categoria').order_by('nombre')
    serializer_class = ProductoSerializer
    search_fields = ['nombre', 'descripcion', 'codigo']
    filterset_fields = ['categoria', 'activo']
    ordering_fields = ['nombre', 'stock_actual', 'precio_venta', 'fecha_creacion']


class ProductoListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Producto.objects.filter(activo=True).select_related('categoria').order_by('nombre')
    serializer_class = ProductoListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion', 'codigo']
    filterset_fields = ['categoria', 'activo']
    ordering_fields = ['nombre', 'stock_actual', 'precio_venta', 'fecha_creacion']
    ordering = ['nombre']


class MovimientoStockViewSet(BaseViewSet):
    queryset = MovimientoStock.objects.select_related('producto__categoria').order_by('-fecha')
    serializer_class = MovimientoStockSerializer
    search_fields = ['producto__nombre', 'motivo', 'tipo']
    filterset_fields = ['producto', 'tipo']
    ordering_fields = ['fecha', 'cantidad']


class MovimientoStockListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MovimientoStock.objects.select_related('producto__categoria').order_by('-fecha')
    serializer_class = MovimientoStockListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['producto__nombre', 'motivo', 'tipo']
    filterset_fields = ['producto', 'tipo']
    ordering_fields = ['fecha', 'cantidad']
    ordering = ['-fecha']