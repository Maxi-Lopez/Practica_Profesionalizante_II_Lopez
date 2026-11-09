from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import TipoServicio, Servicio, ProfesionalServicio, ServicioObraSocial
from .serializers import (
    TipoServicioSerializer,
    ServicioSerializer,
    ServicioListSerializer,
    ProfesionalServicioSerializer,
    ServicioObraSocialSerializer,
)
from personas.permissions import EsAdmin, EsProfesional, EsAdminOProfesional


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-fecha_creacion']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        # Escritura permitida para admin y profesional
        return [EsAdminOProfesional()]

    @action(detail=True, methods=['post'])
    def eliminado_logico(self, request, pk=None):
        obj = self.get_object()
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        obj.activo = False
        if hasattr(obj, 'nombre'):
            obj.nombre = f'delete-{obj.nombre}-{timestamp}'
        obj.save()
        return Response({'detail': 'Eliminado correctamente'}, status=status.HTTP_200_OK)


class TipoServicioViewSet(BaseViewSet):
    queryset = TipoServicio.objects.filter(activo=True).order_by('nombre')
    serializer_class = TipoServicioSerializer
    search_fields = ['nombre', 'descripcion']
    filterset_fields = ['activo']
    ordering_fields = ['nombre']


class ProfesionalServicioViewSet(BaseViewSet):
    queryset = ProfesionalServicio.objects.filter(activo=True).select_related('empleado__persona', 'servicio__tipo_servicio').order_by('-fecha_asignacion')
    serializer_class = ProfesionalServicioSerializer
    search_fields = ['empleado__persona__nombre', 'empleado__persona__apellido', 'servicio__nombre']
    filterset_fields = ['empleado', 'servicio', 'activo']
    ordering_fields = ['fecha_asignacion']


class ServicioObraSocialViewSet(BaseViewSet):
    queryset = ServicioObraSocial.objects.filter(activo=True).select_related('servicio__tipo_servicio', 'obra_social').order_by('-id')
    serializer_class = ServicioObraSocialSerializer
    search_fields = ['servicio__nombre', 'obra_social__nombre', 'codigo_obra_social']
    filterset_fields = ['servicio', 'obra_social', 'activo']
    ordering_fields = ['servicio', 'obra_social']


class ServicioViewSet(BaseViewSet):
    queryset = Servicio.objects.filter(activo=True).select_related(
        'tipo_servicio'
    ).prefetch_related(
        'profesionales__empleado__persona',
        'obras_sociales__obra_social'
    ).order_by('nombre')
    serializer_class = ServicioSerializer
    search_fields = ['nombre', 'descripcion', 'tipo_servicio__nombre']
    filterset_fields = ['tipo_servicio', 'activo']
    ordering_fields = ['nombre', 'precio_base', 'duracion_minutos', 'fecha_creacion']


class ServicioListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Servicio.objects.filter(activo=True).select_related(
        'tipo_servicio'
    ).prefetch_related(
        'profesionales__empleado__persona',
        'obras_sociales__obra_social'
    ).order_by('nombre')
    serializer_class = ServicioListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion', 'tipo_servicio__nombre']
    filterset_fields = ['tipo_servicio', 'activo']
    ordering_fields = ['nombre', 'precio_base', 'duracion_minutos', 'fecha_creacion']
    ordering = ['nombre']