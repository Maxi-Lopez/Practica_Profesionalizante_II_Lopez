from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    PlanTratamiento, ObjetivoTratamiento, ActividadPlan,
    HistorialMedico, EvolucionSemanal, RegistroActividad, NotaImportante
)
from .serializers import (
    PlanTratamientoSerializer,
    PlanTratamientoListSerializer,
    ObjetivoTratamientoSerializer,
    ActividadPlanSerializer,
    HistorialMedicoSerializer,
    EvolucionSemanalSerializer,
    RegistroActividadSerializer,
    NotaImportanteSerializer,
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
        elif hasattr(obj, 'descripcion'):
            obj.descripcion = f'delete-{obj.descripcion[:50]}-{timestamp}'
        elif hasattr(obj, 'titulo'):
            obj.titulo = f'delete-{obj.titulo}-{timestamp}'
        obj.save()
        return Response({'detail': 'Eliminado correctamente'}, status=status.HTTP_200_OK)


class PlanTratamientoViewSet(BaseViewSet):
    queryset = PlanTratamiento.objects.filter(activo=True).select_related(
        'paciente__persona__localidad__provincia__pais'
    ).prefetch_related(
        'objetivos',
        'actividades__servicio',
        'evoluciones__profesional__persona'
    ).order_by('-fecha_inicio')
    serializer_class = PlanTratamientoSerializer
    search_fields = ['nombre', 'descripcion', 'paciente__persona__nombre', 'paciente__persona__apellido']
    filterset_fields = ['activo', 'paciente', 'fecha_inicio']
    ordering_fields = ['fecha_inicio', 'fecha_fin', 'fecha_creacion']


class PlanTratamientoListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PlanTratamiento.objects.filter(activo=True).select_related(
        'paciente__persona__localidad__provincia__pais'
    ).prefetch_related(
        'objetivos',
        'actividades__servicio',
        'evoluciones__profesional__persona'
    ).order_by('-fecha_inicio')
    serializer_class = PlanTratamientoListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion', 'paciente__persona__nombre', 'paciente__persona__apellido']
    filterset_fields = ['activo', 'paciente', 'fecha_inicio']
    ordering_fields = ['fecha_inicio', 'fecha_fin', 'fecha_creacion']
    ordering = ['-fecha_inicio']


class ObjetivoTratamientoViewSet(BaseViewSet):
    queryset = ObjetivoTratamiento.objects.filter(activo=True).select_related('plan_tratamiento__paciente__persona').order_by('-fecha_creacion')
    serializer_class = ObjetivoTratamientoSerializer
    search_fields = ['descripcion', 'plan_tratamiento__nombre']
    filterset_fields = ['plan_tratamiento', 'cumplido', 'activo']
    ordering_fields = ['fecha_creacion']


class ActividadPlanViewSet(BaseViewSet):
    queryset = ActividadPlan.objects.filter(activo=True).select_related('plan_tratamiento__paciente__persona', 'servicio__tipo_servicio').order_by('-fecha_creacion')
    serializer_class = ActividadPlanSerializer
    search_fields = ['descripcion', 'plan_tratamiento__nombre', 'servicio__nombre']
    filterset_fields = ['plan_tratamiento', 'servicio', 'activo']
    ordering_fields = ['fecha_creacion', 'frecuencia_semanal']


class HistorialMedicoViewSet(BaseViewSet):
    queryset = HistorialMedico.objects.select_related('paciente__persona', 'profesional__persona').order_by('-fecha')
    serializer_class = HistorialMedicoSerializer
    search_fields = ['paciente__persona__nombre', 'paciente__persona__apellido', 'profesional__persona__nombre', 'profesional__persona__apellido', 'descripcion']
    filterset_fields = ['paciente', 'profesional']
    ordering_fields = ['fecha', 'fecha_creacion']


class EvolucionSemanalViewSet(BaseViewSet):
    queryset = EvolucionSemanal.objects.select_related(
        'paciente__persona',
        'plan_tratamiento',
        'profesional__persona'
    ).order_by('-fecha')
    serializer_class = EvolucionSemanalSerializer
    search_fields = ['paciente__persona__nombre', 'paciente__persona__apellido', 'plan_tratamiento__nombre', 'profesional__persona__nombre', 'descripcion']
    filterset_fields = ['paciente', 'plan_tratamiento', 'profesional', 'fecha']
    ordering_fields = ['fecha', 'fecha_creacion']


class RegistroActividadViewSet(BaseViewSet):
    queryset = RegistroActividad.objects.select_related(
        'paciente__persona',
        'actividad__plan_tratamiento',
        'actividad__servicio',
        'profesional__persona'
    ).order_by('-fecha')
    serializer_class = RegistroActividadSerializer
    search_fields = ['paciente__persona__nombre', 'paciente__persona__apellido', 'actividad__descripcion', 'profesional__persona__nombre']
    filterset_fields = ['paciente', 'actividad', 'profesional', 'realizado', 'fecha']
    ordering_fields = ['fecha', 'fecha_creacion']


class NotaImportanteViewSet(BaseViewSet):
    queryset = NotaImportante.objects.select_related('paciente__persona', 'profesional__persona').order_by('-fecha')
    serializer_class = NotaImportanteSerializer
    search_fields = ['paciente__persona__nombre', 'paciente__persona__apellido', 'profesional__persona__nombre', 'titulo', 'descripcion']
    filterset_fields = ['paciente', 'profesional']
    ordering_fields = ['fecha']