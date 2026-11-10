from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    ObraSocial, TipoDiagnostico, Diagnostico, Paciente,
    ResponsablePaciente, PacienteDiagnostico,
    Sala, AreaInterdisciplinaria, DiagnosticoArea, SeguimientoTrimestral
)
from .serializers import (
    ObraSocialSerializer,
    TipoDiagnosticoSerializer,
    DiagnosticoSerializer,
    PacienteSerializer,
    PacienteListSerializer,
    ResponsablePacienteSerializer,
    PacienteDiagnosticoSerializer,
    SalaSerializer,
    AreaInterdisciplinariaSerializer,
    DiagnosticoAreaSerializer,
    SeguimientoTrimestralSerializer,
)
from core.permissions import (
    EsAdmin, EsOrientador, EsProfesional, EsRecepcionista,
    EsAdminOProfesional, EsAdminProfesionalRecepcionista,
    PuedeVerDiagnosticoArea, PuedeVerSeguimientoTrimestral
)
from rest_framework.permissions import IsAuthenticated


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-fecha_creacion']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        # Escritura permitida para admin, profesional, orientador y recepcionista
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


class SalaViewSet(BaseViewSet):
    queryset = Sala.objects.filter(activo=True).select_related('orientador__persona').order_by('nombre')
    serializer_class = SalaSerializer
    search_fields = ['nombre', 'orientador__persona__nombre', 'orientador__persona__apellido']
    filterset_fields = ['activo', 'orientador']
    ordering_fields = ['nombre', 'fecha_creacion']


class AreaInterdisciplinariaViewSet(BaseViewSet):
    queryset = AreaInterdisciplinaria.objects.filter(activo=True).order_by('nombre')
    serializer_class = AreaInterdisciplinariaSerializer
    search_fields = ['nombre', 'descripcion']
    filterset_fields = ['activo']
    ordering_fields = ['nombre', 'fecha_creacion']


class DiagnosticoAreaViewSet(BaseViewSet):
    permission_classes = [PuedeVerDiagnosticoArea]
    serializer_class = DiagnosticoAreaSerializer
    search_fields = ['paciente__persona__nombre', 'paciente__persona__apellido', 'diagnostico']
    filterset_fields = ['paciente', 'area', 'activo']
    ordering_fields = ['fecha', 'fecha_creacion']
    ordering = ['-fecha']

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return DiagnosticoArea.objects.none()
        if user.is_superuser or user.rol in ['admin', 'orientador']:
            return DiagnosticoArea.objects.filter(activo=True).select_related(
                'paciente__persona', 'area', 'profesional__persona'
            )
        if user.rol == 'profesional':
            return DiagnosticoArea.objects.filter(activo=True, area=user.area).select_related(
                'paciente__persona', 'area', 'profesional__persona'
            )
        return DiagnosticoArea.objects.none()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [PuedeVerDiagnosticoArea()]
        return [EsAdminProfesionalRecepcionista()]


class SeguimientoTrimestralViewSet(BaseViewSet):
    permission_classes = [PuedeVerSeguimientoTrimestral]
    serializer_class = SeguimientoTrimestralSerializer
    search_fields = ['paciente__persona__nombre', 'paciente__persona__apellido', 'observaciones']
    filterset_fields = ['paciente', 'area', 'activo', 'es_intervencion_mensual']
    ordering_fields = ['fecha', 'fecha_creacion']
    ordering = ['-fecha']

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return SeguimientoTrimestral.objects.none()
        if user.is_superuser or user.rol in ['admin', 'orientador']:
            return SeguimientoTrimestral.objects.filter(activo=True).select_related(
                'paciente__persona', 'area', 'profesional__persona'
            )
        if user.rol == 'profesional':
            return SeguimientoTrimestral.objects.filter(activo=True, area=user.area).select_related(
                'paciente__persona', 'area', 'profesional__persona'
            )
        return SeguimientoTrimestral.objects.none()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [PuedeVerSeguimientoTrimestral()]
        return [EsAdminProfesionalRecepcionista()]


class PacienteViewSet(BaseViewSet):
    queryset = Paciente.objects.filter(activo=True).select_related(
        'persona__localidad__provincia__pais',
        'obra_social',
        'sala'
    ).prefetch_related(
        'diagnosticos__diagnostico__tipo',
        'responsables__persona'
    ).order_by('persona__apellido', 'persona__nombre')
    serializer_class = PacienteSerializer
    search_fields = ['persona__nombre', 'persona__apellido', 'persona__dni', 'historia_clinica', 'nro_afiliado']
    filterset_fields = ['activo', 'obra_social', 'persona__localidad', 'persona__localidad__provincia', 'sala', 'estado_admision']
    ordering_fields = ['persona__apellido', 'persona__nombre', 'historia_clinica', 'fecha_ingreso', 'fecha_creacion']

    def get_permissions(self):
        """Pacientes requiere autenticación para todas las operaciones."""
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [EsAdminProfesionalRecepcionista()]


class PacienteListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Paciente.objects.filter(activo=True).select_related(
        'persona__localidad__provincia__pais',
        'obra_social',
        'sala'
    ).prefetch_related(
        'diagnosticos__diagnostico__tipo',
        'responsables__persona'
    ).order_by('persona__apellido', 'persona__nombre')
    serializer_class = PacienteListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['persona__nombre', 'persona__apellido', 'persona__dni', 'historia_clinica', 'nro_afiliado']
    filterset_fields = ['activo', 'obra_social', 'persona__localidad', 'persona__localidad__provincia', 'sala', 'estado_admision']
    ordering_fields = ['persona__apellido', 'persona__nombre', 'historia_clinica', 'fecha_ingreso', 'fecha_creacion']
    ordering = ['persona__apellido', 'persona__nombre']