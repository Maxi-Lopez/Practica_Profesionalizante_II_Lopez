from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Pais, Provincia, Localidad, Persona
from .serializers import (
    PaisSerializer,
    ProvinciaSerializer,
    LocalidadSerializer,
    PersonaSerializer,
    PersonaListSerializer,
)
from .permissions import EsAdminOProfesional


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-fecha_creacion']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [EsAdminOProfesional()]

    @action(detail=True, methods=['post'])
    def eliminado_logico(self, request, pk=None):
        obj = self.get_object()
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        obj.activo = False
        if hasattr(obj, 'nombre'):
            obj.nombre = f'delete-{obj.nombre}-{timestamp}'
        elif hasattr(obj, 'dni'):
            obj.dni = f'delete-{obj.dni}-{timestamp}'
        obj.save()
        return Response({'detail': 'Eliminado correctamente'}, status=status.HTTP_200_OK)


class PaisViewSet(BaseViewSet):
    queryset = Pais.objects.filter(activo=True).order_by('nombre')
    serializer_class = PaisSerializer
    search_fields = ['nombre']
    filterset_fields = ['activo']
    ordering_fields = ['nombre', 'fecha_creacion']


class ProvinciaViewSet(BaseViewSet):
    queryset = Provincia.objects.filter(activo=True).select_related('pais').order_by('nombre')
    serializer_class = ProvinciaSerializer
    search_fields = ['nombre']
    filterset_fields = ['pais', 'activo']
    ordering_fields = ['nombre', 'fecha_creacion']


class LocalidadViewSet(BaseViewSet):
    queryset = Localidad.objects.filter(activo=True).select_related('provincia__pais').order_by('nombre')
    serializer_class = LocalidadSerializer
    search_fields = ['nombre', 'codigo_postal']
    filterset_fields = ['provincia', 'activo']
    ordering_fields = ['nombre', 'codigo_postal', 'fecha_creacion']


class PersonaViewSet(BaseViewSet):
    queryset = Persona.objects.filter(activo=True).select_related(
        'localidad__provincia__pais'
    ).order_by('apellido', 'nombre')
    serializer_class = PersonaSerializer
    search_fields = ['nombre', 'apellido', 'dni']
    filterset_fields = ['activo', 'localidad', 'localidad__provincia', 'localidad__provincia__pais']
    ordering_fields = ['apellido', 'nombre', 'dni', 'fecha_creacion']


class PersonaListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Persona.objects.filter(activo=True).select_related(
        'localidad__provincia__pais'
    ).prefetch_related('telefonos', 'emails').order_by('apellido', 'nombre')
    serializer_class = PersonaListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'apellido', 'dni']
    filterset_fields = ['activo', 'localidad', 'localidad__provincia', 'localidad__provincia__pais']
    ordering_fields = ['apellido', 'nombre', 'dni', 'fecha_creacion']
    ordering = ['apellido', 'nombre']