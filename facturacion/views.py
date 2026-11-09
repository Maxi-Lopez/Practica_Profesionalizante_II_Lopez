from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import FacturaVenta, DetalleVenta, Pago, EstadoFactura
from .serializers import (
    FacturaVentaSerializer,
    FacturaVentaListSerializer,
    DetalleVentaSerializer,
    PagoSerializer,
)
from personas.permissions import EsAdmin, EsProfesional, EsRecepcionista, EsAdminProfesionalRecepcionista


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-fecha']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        # Escritura permitida para admin, profesional y recepcionista
        return [EsAdminProfesionalRecepcionista()]

    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        obj = self.get_object()
        obj.estado = EstadoFactura.ANULADA
        obj.save()
        return Response({'detail': 'Factura anulada correctamente'}, status=status.HTTP_200_OK)


class FacturaVentaViewSet(BaseViewSet):
    queryset = FacturaVenta.objects.select_related(
        'paciente__persona__localidad__provincia__pais',
        'obra_social'
    ).prefetch_related(
        'detalles__servicio__tipo_servicio',
        'pagos'
    ).order_by('-fecha')
    serializer_class = FacturaVentaSerializer
    search_fields = ['numero_factura', 'paciente__persona__nombre', 'paciente__persona__apellido', 'paciente__persona__dni']
    filterset_fields = ['estado', 'paciente', 'obra_social', 'fecha']
    ordering_fields = ['fecha', 'numero_factura', 'total', 'estado']


class FacturaVentaListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FacturaVenta.objects.select_related(
        'paciente__persona__localidad__provincia__pais',
        'obra_social'
    ).prefetch_related(
        'detalles__servicio__tipo_servicio',
        'pagos'
    ).order_by('-fecha')
    serializer_class = FacturaVentaListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['numero_factura', 'paciente__persona__nombre', 'paciente__persona__apellido', 'paciente__persona__dni']
    filterset_fields = ['estado', 'paciente', 'obra_social', 'fecha']
    ordering_fields = ['fecha', 'numero_factura', 'total', 'estado']
    ordering = ['-fecha']


class DetalleVentaViewSet(BaseViewSet):
    queryset = DetalleVenta.objects.select_related('factura__paciente__persona', 'servicio__tipo_servicio')
    serializer_class = DetalleVentaSerializer
    search_fields = ['descripcion', 'factura__numero_factura']
    filterset_fields = ['factura', 'servicio']
    ordering_fields = ['id']


class PagoViewSet(BaseViewSet):
    queryset = Pago.objects.select_related('factura__paciente__persona').order_by('-fecha')
    serializer_class = PagoSerializer
    search_fields = ['factura__numero_factura', 'referencia']
    filterset_fields = ['factura', 'medio_pago', 'anulado']
    ordering_fields = ['fecha', 'monto']