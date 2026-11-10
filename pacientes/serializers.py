from rest_framework import serializers
from .models import (
    ObraSocial, Paciente, ResponsablePaciente,
    TipoDiagnostico, Diagnostico, PacienteDiagnostico,
    Sala, AreaInterdisciplinaria, DiagnosticoArea, SeguimientoTrimestral
)
from personas.serializers import PersonaSerializer
from empleados.serializers import EmpleadoSerializer


class ObraSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObraSocial
        fields = ['id', 'nombre', 'codigo', 'telefono', 'email', 'cuit', 'activo', 'fecha_creacion', 'fecha_actualizacion']
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'activo']


class TipoDiagnosticoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDiagnostico
        fields = ['id', 'nombre', 'activo']
        read_only_fields = ['id', 'activo']


class DiagnosticoSerializer(serializers.ModelSerializer):
    tipo = TipoDiagnosticoSerializer(read_only=True)
    tipo_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoDiagnostico.objects.all(),
        source='tipo',
        write_only=True,
        required=False,
    )

    class Meta:
        model = Diagnostico
        fields = ['id', 'tipo', 'tipo_id', 'nombre', 'descripcion', 'codigo_cie10', 'activo']
        read_only_fields = ['id', 'activo']


class PacienteDiagnosticoSerializer(serializers.ModelSerializer):
    diagnostico = DiagnosticoSerializer(read_only=True)
    diagnostico_id = serializers.PrimaryKeyRelatedField(
        queryset=Diagnostico.objects.all(),
        source='diagnostico',
        write_only=True,
        required=False,
    )

    class Meta:
        model = PacienteDiagnostico
        fields = ['id', 'paciente', 'diagnostico', 'diagnostico_id', 'tipo', 'fecha_registro', 'activo']
        read_only_fields = ['id', 'fecha_registro', 'activo']


class ResponsablePacienteSerializer(serializers.ModelSerializer):
    persona = PersonaSerializer(read_only=True)
    persona_id = serializers.PrimaryKeyRelatedField(
        queryset=PersonaSerializer.Meta.model.objects.all(),
        source='persona',
        write_only=True,
        required=False,
    )

    class Meta:
        model = ResponsablePaciente
        fields = ['id', 'paciente', 'persona', 'persona_id', 'parentesco', 'es_principal', 'activo', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion', 'activo']


class SalaSerializer(serializers.ModelSerializer):
    orientador = EmpleadoSerializer(read_only=True)
    orientador_id = serializers.PrimaryKeyRelatedField(
        queryset=EmpleadoSerializer.Meta.model.objects.all(),
        source='orientador',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Sala
        fields = ['id', 'nombre', 'orientador', 'orientador_id', 'planificacion_actividades', 'activo', 'fecha_creacion', 'fecha_actualizacion']
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'activo']


class AreaInterdisciplinariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaInterdisciplinaria
        fields = ['id', 'nombre', 'descripcion', 'activo', 'fecha_creacion', 'fecha_actualizacion']
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'activo']


class DiagnosticoAreaSerializer(serializers.ModelSerializer):
    area = AreaInterdisciplinariaSerializer(read_only=True)
    area_id = serializers.PrimaryKeyRelatedField(
        queryset=AreaInterdisciplinaria.objects.all(),
        source='area',
        write_only=True,
    )
    profesional = EmpleadoSerializer(read_only=True)
    profesional_id = serializers.PrimaryKeyRelatedField(
        queryset=EmpleadoSerializer.Meta.model.objects.all(),
        source='profesional',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = DiagnosticoArea
        fields = ['id', 'paciente', 'area', 'area_id', 'fecha', 'diagnostico', 'profesional', 'profesional_id', 'activo', 'fecha_creacion', 'fecha_actualizacion']
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'activo']


class SeguimientoTrimestralSerializer(serializers.ModelSerializer):
    area = AreaInterdisciplinariaSerializer(read_only=True)
    area_id = serializers.PrimaryKeyRelatedField(
        queryset=AreaInterdisciplinaria.objects.all(),
        source='area',
        write_only=True,
    )
    profesional = EmpleadoSerializer(read_only=True)
    profesional_id = serializers.PrimaryKeyRelatedField(
        queryset=EmpleadoSerializer.Meta.model.objects.all(),
        source='profesional',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = SeguimientoTrimestral
        fields = ['id', 'paciente', 'area', 'area_id', 'fecha', 'observaciones', 'profesional', 'profesional_id', 'es_intervencion_mensual', 'activo', 'fecha_creacion', 'fecha_actualizacion']
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'activo']


class PacienteSerializer(serializers.ModelSerializer):
    persona_id = serializers.PrimaryKeyRelatedField(
        queryset=PersonaSerializer.Meta.model.objects.all(),
        source='persona',
        write_only=True,
        required=False,
        allow_null=True,
    )
    obra_social_id = serializers.PrimaryKeyRelatedField(
        queryset=ObraSocial.objects.all(),
        source='obra_social',
        write_only=True,
        required=False,
        allow_null=True,
    )
    sala_id = serializers.PrimaryKeyRelatedField(
        queryset=Sala.objects.all(),
        source='sala',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Paciente
        fields = [
            'id',
            'persona',
            'persona_id',
            'historia_clinica',
            'numero_cud',
            'fecha_vencimiento_cud',
            'aviso_vencimiento_cud',
            'figura_apoyo_nombre',
            'figura_apoyo_telefono',
            'pases_transporte_vencimiento',
            'obra_social',
            'obra_social_id',
            'nro_afiliado',
            'fecha_ingreso',
            'fecha_baja',
            'sala',
            'sala_id',
            'estado_admision',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'activo']

    def validate_historia_clinica(self, value):
        if not value:
            return value
        qs = Paciente.objects.filter(historia_clinica=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un paciente con esta historia clínica.")
        return value


class PacienteListSerializer(PacienteSerializer):
    persona = PersonaSerializer(read_only=True)
    obra_social = ObraSocialSerializer(read_only=True)
    sala = SalaSerializer(read_only=True)
    diagnosticos = PacienteDiagnosticoSerializer(many=True, read_only=True)
    responsables = ResponsablePacienteSerializer(many=True, read_only=True)

    class Meta(PacienteSerializer.Meta):
        fields = PacienteSerializer.Meta.fields + ['persona', 'obra_social', 'sala', 'diagnosticos', 'responsables']