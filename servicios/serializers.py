from rest_framework import serializers
from .models import TipoServicio, Servicio, ProfesionalServicio, ServicioObraSocial
from empleados.serializers import EmpleadoListSerializer
from pacientes.serializers import ObraSocialSerializer


class TipoServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoServicio
        fields = ['id', 'nombre', 'descripcion', 'activo']
        read_only_fields = ['id', 'activo']


class ProfesionalServicioSerializer(serializers.ModelSerializer):
    empleado = EmpleadoListSerializer(read_only=True)
    empleado_id = serializers.PrimaryKeyRelatedField(
        queryset=EmpleadoListSerializer.Meta.model.objects.all(),
        source='empleado',
        write_only=True,
        required=False,
    )

    class Meta:
        model = ProfesionalServicio
        fields = ['id', 'empleado', 'empleado_id', 'servicio', 'activo', 'fecha_asignacion']
        read_only_fields = ['id', 'fecha_asignacion', 'activo']


class ServicioObraSocialSerializer(serializers.ModelSerializer):
    obra_social = ObraSocialSerializer(read_only=True)
    obra_social_id = serializers.PrimaryKeyRelatedField(
        queryset=ObraSocialSerializer.Meta.model.objects.all(),
        source='obra_social',
        write_only=True,
        required=False,
    )

    class Meta:
        model = ServicioObraSocial
        fields = ['id', 'servicio', 'obra_social', 'obra_social_id', 'precio_autorizado', 'codigo_obra_social', 'activo']
        read_only_fields = ['id', 'activo']


class ServicioSerializer(serializers.ModelSerializer):
    tipo_servicio_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoServicio.objects.all(),
        source='tipo_servicio',
        write_only=True,
        required=False,
    )

    class Meta:
        model = Servicio
        fields = [
            'id',
            'tipo_servicio',
            'tipo_servicio_id',
            'nombre',
            'descripcion',
            'precio_base',
            'duracion_minutos',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'activo']


class ServicioListSerializer(ServicioSerializer):
    tipo_servicio = TipoServicioSerializer(read_only=True)
    profesionales = ProfesionalServicioSerializer(many=True, read_only=True)
    obras_sociales = ServicioObraSocialSerializer(many=True, read_only=True)

    class Meta(ServicioSerializer.Meta):
        fields = ServicioSerializer.Meta.fields + ['tipo_servicio', 'profesionales', 'obras_sociales']