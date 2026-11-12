from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Documento
from .serializers import DocumentoSerializer, DocumentoListSerializer
from core.permissions import EsAdminProfesionalRecepcionista


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-fecha_creacion']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [EsAdminProfesionalRecepcionista()]

    @action(detail=True, methods=['post'])
    def eliminado_logico(self, request, pk=None):
        obj = self.get_object()
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        obj.activo = False
        if hasattr(obj, 'nombre'):
            obj.nombre = f'delete-{obj.nombre}-{timestamp}'
        obj.save()
        return Response({'detail': 'Eliminado correctamente'}, status=status.HTTP_200_OK)


class DocumentoViewSet(BaseViewSet):
    queryset = Documento.objects.select_related('persona__localidad__provincia__pais').filter(activo=True).order_by('-fecha_creacion')
    serializer_class = DocumentoSerializer
    search_fields = ['nombre', 'descripcion', 'persona__nombre', 'persona__apellido', 'persona__dni']
    filterset_fields = ['persona', 'tipo', 'activo']
    ordering_fields = ['fecha_documento', 'fecha_vencimiento', 'fecha_creacion']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return DocumentoListSerializer
        return DocumentoSerializer


class DocumentoListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Documento.objects.select_related('persona__localidad__provincia__pais').filter(activo=True).order_by('-fecha_creacion')
    serializer_class = DocumentoListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion', 'persona__nombre', 'persona__apellido', 'persona__dni']
    filterset_fields = ['persona', 'tipo', 'activo']
    ordering_fields = ['fecha_documento', 'fecha_vencimiento', 'fecha_creacion']
    ordering = ['-fecha_creacion']