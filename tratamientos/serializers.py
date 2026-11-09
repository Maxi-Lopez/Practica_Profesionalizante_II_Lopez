from rest_framework import serializers
from .models import (
    PlanTratamiento, ObjetivoTratamiento, ActividadPlan,
    HistorialMedico, EvolucionSemanal, RegistroActividad, NotaImportante
)
from pacientes.serializers import PacienteListSerializer
from empleados.serializers import EmpleadoListSerializer
from servicios.serializers import ServicioListSerializer


class ObjetivoTratamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjetivoTratamiento
        fields = ['id', 'plan_tratamiento', 'descripcion', 'cumplido', 'activo', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion', 'activo']


class ActividadPlanSerializer(serializers.ModelSerializer):
    servicio = ServicioListSerializer(read_only=True)
    servicio_id = serializers.PrimaryKeyRelatedField(
        queryset=ServicioListSerializer.Meta.model.objects.all(),
        source='servicio',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ActividadPlan
        fields = ['id', 'plan_tratamiento', 'servicio', 'servicio_id', 'descripcion', 'frecuencia_semanal', 'activo', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion', 'activo']


class HistorialMedicoSerializer(serializers.ModelSerializer):
    paciente = PacienteListSerializer(read_only=True)
    paciente_id = serializers.PrimaryKeyRelatedField(
        queryset=PacienteListSerializer.Meta.model.objects.all(),
        source='paciente',
        write_only=True,
        required=False,
    )
    profesional = EmpleadoListSerializer(read_only=True)
    profesional_id = serializers.PrimaryKeyRelatedField(
        queryset=EmpleadoListSerializer.Meta.model.objects.all(),
        source='profesional',
        write_only=True,
        required=False,
    )

    class Meta:
        model = HistorialMedico
        fields = ['id', 'paciente', 'paciente_id', 'profesional', 'profesional_id', 'fecha', 'descripcion', 'observaciones', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']


class EvolucionSemanalSerializer(serializers.ModelSerializer):
    paciente = PacienteListSerializer(read_only=True)
    paciente_id = serializers.PrimaryKeyRelatedField(
        queryset=PacienteListSerializer.Meta.model.objects.all(),
        source='paciente',
        write_only=True,
        required=False,
    )
    plan_tratamiento = serializers.SerializerMethodField()
    plan_tratamiento_id = serializers.PrimaryKeyRelatedField(
        queryset=PlanTratamiento.objects.all(),
        source='plan_tratamiento',
        write_only=True,
        required=False,
        allow_null=True,
    )
    profesional = EmpleadoListSerializer(read_only=True)
    profesional_id = serializers.PrimaryKeyRelatedField(
        queryset=EmpleadoListSerializer.Meta.model.objects.all(),
        source='profesional',
        write_only=True,
        required=False,
    )

    class Meta:
        model = EvolucionSemanal
        fields = ['id', 'paciente', 'paciente_id', 'plan_tratamiento', 'plan_tratamiento_id', 'profesional', 'profesional_id', 'fecha', 'descripcion', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']

    def get_plan_tratamiento(self, obj):
        if obj.plan_tratamiento:
            return {
                'id': obj.plan_tratamiento.id,
                'nombre': obj.plan_tratamiento.nombre,
            }
        return None


class RegistroActividadSerializer(serializers.ModelSerializer):
    paciente = PacienteListSerializer(read_only=True)
    paciente_id = serializers.PrimaryKeyRelatedField(
        queryset=PacienteListSerializer.Meta.model.objects.all(),
        source='paciente',
        write_only=True,
        required=False,
    )
    actividad = ActividadPlanSerializer(read_only=True)
    actividad_id = serializers.PrimaryKeyRelatedField(
        queryset=ActividadPlanSerializer.Meta.model.objects.all(),
        source='actividad',
        write_only=True,
        required=False,
    )
    profesional = EmpleadoListSerializer(read_only=True)
    profesional_id = serializers.PrimaryKeyRelatedField(
        queryset=EmpleadoListSerializer.Meta.model.objects.all(),
        source='profesional',
        write_only=True,
        required=False,
    )

    class Meta:
        model = RegistroActividad
        fields = ['id', 'paciente', 'paciente_id', 'actividad', 'actividad_id', 'profesional', 'profesional_id', 'fecha', 'descripcion', 'realizado', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']


class NotaImportanteSerializer(serializers.ModelSerializer):
    paciente = PacienteListSerializer(read_only=True)
    paciente_id = serializers.PrimaryKeyRelatedField(
        queryset=PacienteListSerializer.Meta.model.objects.all(),
        source='paciente',
        write_only=True,
        required=False,
    )
    profesional = EmpleadoListSerializer(read_only=True)
    profesional_id = serializers.PrimaryKeyRelatedField(
        queryset=EmpleadoListSerializer.Meta.model.objects.all(),
        source='profesional',
        write_only=True,
        required=False,
    )

    class Meta:
        model = NotaImportante
        fields = ['id', 'paciente', 'paciente_id', 'profesional', 'profesional_id', 'titulo', 'descripcion', 'fecha']
        read_only_fields = ['id', 'fecha']


class PlanTratamientoSerializer(serializers.ModelSerializer):
    paciente_id = serializers.PrimaryKeyRelatedField(
        queryset=PacienteListSerializer.Meta.model.objects.all(),
        source='paciente',
        write_only=True,
        required=False,
    )

    class Meta:
        model = PlanTratamiento
        fields = [
            'id',
            'paciente',
            'paciente_id',
            'nombre',
            'descripcion',
            'fecha_inicio',
            'fecha_fin',
            'observaciones',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'activo']

    def validate(self, attrs):
        fecha_inicio = attrs.get('fecha_inicio')
        fecha_fin = attrs.get('fecha_fin')

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError({
                'fecha_fin': 'La fecha de fin debe ser mayor o igual a la fecha de inicio.'
            })

        return attrs


class PlanTratamientoListSerializer(PlanTratamientoSerializer):
    paciente = PacienteListSerializer(read_only=True)
    objetivos = ObjetivoTratamientoSerializer(many=True, read_only=True)
    actividades = ActividadPlanSerializer(many=True, read_only=True)
    evoluciones = EvolucionSemanalSerializer(many=True, read_only=True)

    class Meta(PlanTratamientoSerializer.Meta):
        fields = PlanTratamientoSerializer.Meta.fields + ['paciente', 'objetivos', 'actividades', 'evoluciones']