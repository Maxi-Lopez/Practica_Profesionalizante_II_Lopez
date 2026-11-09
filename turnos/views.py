from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Turno, AsistenciaPaciente, EstadoTurno
from .serializers import TurnoSerializer, TurnoListSerializer, AsistenciaPacienteSerializer
from personas.permissions import EsAdmin, EsProfesional, EsRecepcionista, EsAdminProfesionalRecepcionista


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-fecha', '-hora_inicio']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        # Escritura permitida para admin, profesional y recepcionista
        return [EsAdminProfesionalRecepcionista()]

    @action(detail=True, methods=['post'])
    def eliminado_logico(self, request, pk=None):
        obj = self.get_object()
        obj.activo = False
        obj.save()
        return Response({'detail': 'Eliminado correctamente'}, status=status.HTTP_200_OK)


class TurnoViewSet(BaseViewSet):
    queryset = Turno.objects.select_related(
        'paciente__persona__localidad__provincia__pais',
        'profesional__persona__localidad__provincia__pais',
        'servicio__tipo_servicio',
        'plan_tratamiento'
    ).order_by('-fecha', '-hora_inicio')
    serializer_class = TurnoSerializer
    search_fields = ['paciente__persona__nombre', 'paciente__persona__apellido', 'profesional__persona__nombre', 'profesional__persona__apellido', 'servicio__nombre']
    filterset_fields = ['estado', 'paciente', 'profesional', 'servicio', 'fecha', 'plan_tratamiento']
    ordering_fields = ['fecha', 'hora_inicio', 'estado', 'fecha_creacion']


class TurnoListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Turno.objects.select_related(
        'paciente__persona__localidad__provincia__pais',
        'profesional__persona__localidad__provincia__pais',
        'servicio__tipo_servicio',
        'plan_tratamiento'
    ).order_by('-fecha', '-hora_inicio')
    serializer_class = TurnoListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['paciente__persona__nombre', 'paciente__persona__apellido', 'profesional__persona__nombre', 'profesional__persona__apellido', 'servicio__nombre']
    filterset_fields = ['estado', 'paciente', 'profesional', 'servicio', 'fecha', 'plan_tratamiento']
    ordering_fields = ['fecha', 'hora_inicio', 'estado', 'fecha_creacion']
    ordering = ['-fecha', '-hora_inicio']


class AsistenciaPacienteViewSet(BaseViewSet):
    queryset = AsistenciaPaciente.objects.select_related('turno__paciente__persona', 'turno__profesional__persona', 'turno__servicio').order_by('-fecha_registro')
    serializer_class = AsistenciaPacienteSerializer
    search_fields = ['turno__paciente__persona__nombre', 'turno__paciente__persona__apellido']
    filterset_fields = ['turno', 'presente', 'turno__fecha']
    ordering_fields = ['fecha_registro']