from rest_framework import serializers
from .models import Turno, AsistenciaPaciente, EstadoTurno
from pacientes.serializers import PacienteListSerializer
from empleados.serializers import EmpleadoListSerializer
from servicios.serializers import ServicioListSerializer
from tratamientos.models import PlanTratamiento


class TurnoSerializer(serializers.ModelSerializer):
    paciente_id = serializers.PrimaryKeyRelatedField(
        queryset=PacienteListSerializer.Meta.model.objects.all(),
        source='paciente',
        write_only=True,
        required=False,
    )
    profesional_id = serializers.PrimaryKeyRelatedField(
        queryset=EmpleadoListSerializer.Meta.model.objects.all(),
        source='profesional',
        write_only=True,
        required=False,
    )
    servicio_id = serializers.PrimaryKeyRelatedField(
        queryset=ServicioListSerializer.Meta.model.objects.all(),
        source='servicio',
        write_only=True,
        required=False,
    )
    plan_tratamiento_id = serializers.PrimaryKeyRelatedField(
        queryset=PlanTratamiento.objects.all(),
        source='plan_tratamiento',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Turno
        fields = [
            'id',
            'paciente',
            'paciente_id',
            'profesional',
            'profesional_id',
            'servicio',
            'servicio_id',
            'plan_tratamiento',
            'plan_tratamiento_id',
            'fecha',
            'hora_inicio',
            'hora_fin',
            'estado',
            'observaciones',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

    def validate(self, attrs):
        hora_inicio = attrs.get('hora_inicio')
        hora_fin = attrs.get('hora_fin')

        if hora_inicio and hora_fin and hora_fin <= hora_inicio:
            raise serializers.ValidationError({
                'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio.'
            })

        # Validar solapamiento de turnos del profesional
        profesional = attrs.get('profesional')
        fecha = attrs.get('fecha')

        if profesional and fecha and hora_inicio and hora_fin:
            qs = Turno.objects.filter(
                profesional=profesional,
                fecha=fecha,
            ).exclude(estado=EstadoTurno.CANCELADO)

            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)

            # Verificar solapamiento
            for turno_existente in qs:
                if not (hora_fin <= turno_existente.hora_inicio or hora_inicio >= turno_existente.hora_fin):
                    raise serializers.ValidationError({
                        'hora_inicio': 'El profesional ya tiene un turno en ese horario.'
                    })

        return attrs


class TurnoListSerializer(TurnoSerializer):
    paciente = PacienteListSerializer(read_only=True)
    profesional = EmpleadoListSerializer(read_only=True)
    servicio = ServicioListSerializer(read_only=True)
    plan_tratamiento = serializers.SerializerMethodField()

    class Meta(TurnoSerializer.Meta):
        fields = TurnoSerializer.Meta.fields + ['paciente', 'profesional', 'servicio', 'plan_tratamiento']

    def get_plan_tratamiento(self, obj):
        if obj.plan_tratamiento:
            return {
                'id': obj.plan_tratamiento.id,
                'nombre': obj.plan_tratamiento.nombre,
            }
        return None


class AsistenciaPacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsistenciaPaciente
        fields = ['id', 'turno', 'fecha_registro', 'presente', 'hora_llegada', 'observaciones']
        read_only_fields = ['id', 'fecha_registro']