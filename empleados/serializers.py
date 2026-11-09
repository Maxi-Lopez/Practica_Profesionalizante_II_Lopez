from rest_framework import serializers
from .models import Rol, Empleado, EmpleadoRol, HorarioEmpleado, AsistenciaEmpleado
from personas.serializers import PersonaSerializer


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion', 'activo']
        read_only_fields = ['id', 'activo']


class EmpleadoRolSerializer(serializers.ModelSerializer):
    rol = RolSerializer(read_only=True)
    rol_id = serializers.PrimaryKeyRelatedField(
        queryset=Rol.objects.all(),
        source='rol',
        write_only=True,
        required=False,
    )

    class Meta:
        model = EmpleadoRol
        fields = ['id', 'empleado', 'rol', 'rol_id', 'activo', 'fecha_asignacion']
        read_only_fields = ['id', 'fecha_asignacion', 'activo']


class HorarioEmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorarioEmpleado
        fields = ['id', 'empleado', 'dia_semana', 'hora_inicio', 'hora_fin', 'activo']
        read_only_fields = ['id', 'activo']


class AsistenciaEmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsistenciaEmpleado
        fields = ['id', 'empleado', 'fecha', 'hora_entrada', 'hora_salida', 'observaciones', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']


class EmpleadoSerializer(serializers.ModelSerializer):
    persona_id = serializers.PrimaryKeyRelatedField(
        queryset=PersonaSerializer.Meta.model.objects.all(),
        source='persona',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Empleado
        fields = [
            'id',
            'persona',
            'persona_id',
            'matricula',
            'fecha_ingreso',
            'fecha_baja',
            'horas_semanales',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'activo']


class EmpleadoListSerializer(EmpleadoSerializer):
    persona = PersonaSerializer(read_only=True)
    roles = EmpleadoRolSerializer(many=True, read_only=True)
    horarios = HorarioEmpleadoSerializer(many=True, read_only=True)

    class Meta(EmpleadoSerializer.Meta):
        fields = EmpleadoSerializer.Meta.fields + ['persona', 'roles', 'horarios']