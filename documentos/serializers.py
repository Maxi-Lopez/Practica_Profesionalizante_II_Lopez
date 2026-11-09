from rest_framework import serializers
from .models import Documento
from personas.serializers import PersonaListSerializer


class DocumentoSerializer(serializers.ModelSerializer):
    persona_id = serializers.PrimaryKeyRelatedField(
        queryset=PersonaListSerializer.Meta.model.objects.all(),
        source='persona',
        write_only=True,
    )

    class Meta:
        model = Documento
        fields = [
            'id',
            'persona',
            'persona_id',
            'tipo',
            'nombre',
            'archivo',
            'descripcion',
            'fecha_documento',
            'fecha_vencimiento',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'activo']


class DocumentoListSerializer(DocumentoSerializer):
    persona = PersonaListSerializer(read_only=True)

    class Meta(DocumentoSerializer.Meta):
        fields = DocumentoSerializer.Meta.fields + ['persona']