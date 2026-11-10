from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Rol, Empleado, EmpleadoRol, HorarioEmpleado, AsistenciaEmpleado
from .serializers import (
    RolSerializer,
    EmpleadoSerializer,
    EmpleadoListSerializer,
    EmpleadoRolSerializer,
    HorarioEmpleadoSerializer,
    AsistenciaEmpleadoSerializer,
)
from personas.permissions import EsAdmin


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [EsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-fecha_creacion']

    @action(detail=True, methods=['post'])
    def eliminado_logico(self, request, pk=None):
        obj = self.get_object()
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        obj.activo = False
        if hasattr(obj, 'nombre'):
            obj.nombre = f'delete-{obj.nombre}-{timestamp}'
        elif hasattr(obj, 'matricula'):
            obj.matricula = f'delete-{obj.matricula}-{timestamp}'
        obj.save()
        return Response({'detail': 'Eliminado correctamente'}, status=status.HTTP_200_OK)


class RolViewSet(BaseViewSet):
    queryset = Rol.objects.filter(activo=True).order_by('nombre')
    serializer_class = RolSerializer
    search_fields = ['nombre', 'descripcion']
    filterset_fields = ['activo']
    ordering_fields = ['nombre']


class EmpleadoRolViewSet(BaseViewSet):
    queryset = EmpleadoRol.objects.filter(activo=True).select_related('empleado__persona', 'rol').order_by('-fecha_asignacion')
    serializer_class = EmpleadoRolSerializer
    search_fields = ['empleado__persona__nombre', 'empleado__persona__apellido', 'rol__nombre']
    filterset_fields = ['empleado', 'rol', 'activo']
    ordering_fields = ['fecha_asignacion']


class HorarioEmpleadoViewSet(BaseViewSet):
    queryset = HorarioEmpleado.objects.filter(activo=True).select_related('empleado__persona').order_by('empleado', 'dia_semana', 'hora_inicio')
    serializer_class = HorarioEmpleadoSerializer
    search_fields = ['empleado__persona__nombre', 'empleado__persona__apellido']
    filterset_fields = ['empleado', 'dia_semana', 'activo']
    ordering_fields = ['dia_semana', 'hora_inicio']


class AsistenciaEmpleadoViewSet(BaseViewSet):
    queryset = AsistenciaEmpleado.objects.select_related('empleado__persona').order_by('-fecha')
    serializer_class = AsistenciaEmpleadoSerializer
    search_fields = ['empleado__persona__nombre', 'empleado__persona__apellido']
    filterset_fields = ['empleado', 'fecha']
    ordering_fields = ['fecha', 'fecha_creacion']


class EmpleadoViewSet(BaseViewSet):
    queryset = Empleado.objects.filter(activo=True).select_related(
        'persona__localidad__provincia__pais'
    ).prefetch_related(
        'roles__rol',
        'horarios'
    ).order_by('persona__apellido', 'persona__nombre')
    serializer_class = EmpleadoSerializer
    search_fields = ['persona__nombre', 'persona__apellido', 'persona__dni', 'matricula']
    filterset_fields = ['activo', 'persona__localidad', 'persona__localidad__provincia']
    ordering_fields = ['persona__apellido', 'persona__nombre', 'matricula', 'fecha_ingreso', 'fecha_creacion']


class EmpleadoListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Empleado.objects.filter(activo=True).select_related(
        'persona__localidad__provincia__pais'
    ).prefetch_related(
        'roles__rol',
        'horarios'
    ).order_by('persona__apellido', 'persona__nombre')
    serializer_class = EmpleadoListSerializer
    permission_classes = [EsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['persona__nombre', 'persona__apellido', 'persona__dni', 'matricula']
    filterset_fields = ['activo', 'persona__localidad', 'persona__localidad__provincia']
    ordering_fields = ['persona__apellido', 'persona__nombre', 'matricula', 'fecha_ingreso', 'fecha_creacion']
    ordering = ['persona__apellido', 'persona__nombre']