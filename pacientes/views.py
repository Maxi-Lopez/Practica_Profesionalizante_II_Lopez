from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import ObraSocial, TipoDiagnostico, Diagnostico, Paciente, ResponsablePaciente, PacienteDiagnostico
from .serializers import (
    ObraSocialSerializer,
    TipoDiagnosticoSerializer,
    DiagnosticoSerializer,
    PacienteSerializer,
    PacienteListSerializer,
    ResponsablePacienteSerializer,
    PacienteDiagnosticoSerializer,
)
from personas.permissions import EsAdmin, EsProfesional, EsRecepcionista, EsAdminOProfesional, EsAdminProfesionalRecepcionista


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-fecha_creacion']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        # Escritura permitida para admin, profesional y recepcionista
        return [EsAdminProfesionalRecepcionista()]

    @action(detail=True, methods=['post'])
    def eliminado_logico(self, request, pk=None):
        obj = self.get_object()
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        obj.activo = False
        if hasattr(obj, 'nombre'):
            obj.nombre = f'delete-{obj.nombre}-{timestamp}'
        elif hasattr(obj, 'historia_clinica'):
            obj.historia_clinica = f'delete-{obj.historia_clinica}-{timestamp}'
        elif hasattr(obj, 'dni'):
            obj.dni = f'delete-{obj.dni}-{timestamp}'
        obj.save()
        return Response({'detail': 'Eliminado correctamente'}, status=status.HTTP_200_OK)


class ObraSocialViewSet(BaseViewSet):
    queryset = ObraSocial.objects.filter(activo=True).order_by('nombre')
    serializer_class = ObraSocialSerializer
    search_fields = ['nombre', 'codigo', 'cuit']
    filterset_fields = ['activo']
    ordering_fields = ['nombre', 'fecha_creacion']


class TipoDiagnosticoViewSet(BaseViewSet):
    queryset = TipoDiagnostico.objects.filter(activo=True).order_by('nombre')
    serializer_class = TipoDiagnosticoSerializer
    search_fields = ['nombre']
    filterset_fields = ['activo']
    ordering_fields = ['nombre']


class DiagnosticoViewSet(BaseViewSet):
    queryset = Diagnostico.objects.filter(activo=True).select_related('tipo').order_by('nombre')
    serializer_class = DiagnosticoSerializer
    search_fields = ['nombre', 'descripcion', 'codigo_cie10']
    filterset_fields = ['tipo', 'activo']
    ordering_fields = ['nombre', 'fecha_creacion']


class ResponsablePacienteViewSet(BaseViewSet):
    queryset = ResponsablePaciente.objects.filter(activo=True).select_related('persona', 'paciente__persona').order_by('-fecha_creacion')
    serializer_class = ResponsablePacienteSerializer
    search_fields = ['persona__nombre', 'persona__apellido', 'parentesco']
    filterset_fields = ['paciente', 'activo', 'es_principal']
    ordering_fields = ['fecha_creacion']


class PacienteDiagnosticoViewSet(BaseViewSet):
    queryset = PacienteDiagnostico.objects.filter(activo=True).select_related('paciente__persona', 'diagnostico__tipo').order_by('-fecha_registro')
    serializer_class = PacienteDiagnosticoSerializer
    search_fields = ['paciente__persona__nombre', 'paciente__persona__apellido', 'diagnostico__nombre']
    filterset_fields = ['paciente', 'diagnostico', 'tipo', 'activo']
    ordering_fields = ['fecha_registro']


class PacienteViewSet(BaseViewSet):
    queryset = Paciente.objects.filter(activo=True).select_related(
        'persona__localidad__provincia__pais',
        'obra_social'
    ).prefetch_related(
        'diagnosticos__diagnostico__tipo',
        'responsables__persona'
    ).order_by('persona__apellido', 'persona__nombre')
    serializer_class = PacienteSerializer
    search_fields = ['persona__nombre', 'persona__apellido', 'persona__dni', 'historia_clinica', 'nro_afiliado']
    filterset_fields = ['activo', 'obra_social', 'persona__localidad', 'persona__localidad__provincia']
    ordering_fields = ['persona__apellido', 'persona__nombre', 'historia_clinica', 'fecha_ingreso', 'fecha_creacion']


class PacienteListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Paciente.objects.filter(activo=True).select_related(
        'persona__localidad__provincia__pais',
        'obra_social'
    ).prefetch_related(
        'diagnosticos__diagnostico__tipo',
        'responsables__persona'
    ).order_by('persona__apellido', 'persona__nombre')
    serializer_class = PacienteListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['persona__nombre', 'persona__apellido', 'persona__dni', 'historia_clinica', 'nro_afiliado']
    filterset_fields = ['activo', 'obra_social', 'persona__localidad', 'persona__localidad__provincia']
    ordering_fields = ['persona__apellido', 'persona__nombre', 'historia_clinica', 'fecha_ingreso', 'fecha_creacion']
    ordering = ['persona__apellido', 'persona__nombre']