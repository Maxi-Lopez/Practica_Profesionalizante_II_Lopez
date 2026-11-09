from rest_framework import serializers
from .models import Pais, Provincia, Localidad, Persona, Telefono, Email


class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pais
        fields = ['id', 'nombre', 'activo']
        read_only_fields = ['id', 'activo']


class ProvinciaSerializer(serializers.ModelSerializer):
    pais = PaisSerializer(read_only=True)
    pais_id = serializers.PrimaryKeyRelatedField(
        queryset=Pais.objects.all(),
        source='pais',
        write_only=True,
        required=False,
    )

    class Meta:
        model = Provincia
        fields = ['id', 'nombre', 'pais', 'pais_id', 'activo']
        read_only_fields = ['id', 'activo']


class LocalidadSerializer(serializers.ModelSerializer):
    provincia = ProvinciaSerializer(read_only=True)
    provincia_id = serializers.PrimaryKeyRelatedField(
        queryset=Provincia.objects.all(),
        source='provincia',
        write_only=True,
        required=False,
    )

    class Meta:
        model = Localidad
        fields = ['id', 'nombre', 'codigo_postal', 'provincia', 'provincia_id', 'activo']
        read_only_fields = ['id', 'activo']


class TelefonoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Telefono
        fields = ['id', 'persona', 'numero', 'tipo', 'es_principal', 'activo', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion', 'activo']


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = ['id', 'persona', 'direccion_email', 'tipo', 'es_principal', 'activo', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion', 'activo']


class PersonaSerializer(serializers.ModelSerializer):
    localidad_id = serializers.PrimaryKeyRelatedField(
        queryset=Localidad.objects.all(),
        source='localidad',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Persona
        fields = [
            'id',
            'nombre',
            'apellido',
            'dni',
            'fecha_nacimiento',
            'direccion',
            'localidad',
            'localidad_id',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'activo']

    def validate_dni(self, value):
        if not value:
            return value
        qs = Persona.objects.filter(dni=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe una persona con este DNI.")
        return value


class PersonaListSerializer(PersonaSerializer):
    localidad = LocalidadSerializer(read_only=True)
    telefonos = TelefonoSerializer(many=True, read_only=True)
    emails = EmailSerializer(many=True, read_only=True)

    class Meta(PersonaSerializer.Meta):
        fields = PersonaSerializer.Meta.fields + ['localidad', 'telefonos', 'emails']