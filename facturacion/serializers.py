from rest_framework import serializers
from .models import FacturaVenta, DetalleVenta, Pago, EstadoFactura
from pacientes.serializers import PacienteListSerializer, ObraSocialSerializer
from servicios.serializers import ServicioListSerializer


class DetalleVentaSerializer(serializers.ModelSerializer):
    servicio = ServicioListSerializer(read_only=True)
    servicio_id = serializers.PrimaryKeyRelatedField(
        queryset=ServicioListSerializer.Meta.model.objects.all(),
        source='servicio',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = DetalleVenta
        fields = ['id', 'factura', 'servicio', 'servicio_id', 'descripcion', 'cantidad', 'precio_unitario', 'subtotal']
        read_only_fields = ['id', 'subtotal']

    def validate(self, attrs):
        cantidad = attrs.get('cantidad', 1)
        precio_unitario = attrs.get('precio_unitario')
        if precio_unitario is not None:
            attrs['subtotal'] = cantidad * precio_unitario
        return attrs


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ['id', 'factura', 'fecha', 'monto', 'medio_pago', 'referencia', 'observaciones', 'anulado']
        read_only_fields = ['id', 'fecha']


class FacturaVentaSerializer(serializers.ModelSerializer):
    paciente_id = serializers.PrimaryKeyRelatedField(
        queryset=PacienteListSerializer.Meta.model.objects.all(),
        source='paciente',
        write_only=True,
        required=False,
    )
    obra_social_id = serializers.PrimaryKeyRelatedField(
        queryset=ObraSocialSerializer.Meta.model.objects.all(),
        source='obra_social',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = FacturaVenta
        fields = [
            'id',
            'paciente',
            'paciente_id',
            'obra_social',
            'obra_social_id',
            'numero_factura',
            'fecha',
            'estado',
            'subtotal',
            'descuento',
            'total',
            'observaciones',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha', 'fecha_actualizacion', 'total']

    def validate(self, attrs):
        from django.utils import timezone
        
        fecha = attrs.get('fecha')
        if fecha and fecha > timezone.now():
            raise serializers.ValidationError({
                'fecha': 'La fecha no puede ser futura.'
            })

        subtotal = attrs.get('subtotal', 0)
        descuento = attrs.get('descuento', 0)
        total = attrs.get('total', 0)

        if total != subtotal - descuento:
            raise serializers.ValidationError({
                'total': 'El total debe ser igual a subtotal - descuento.'
            })

        return attrs


class FacturaVentaListSerializer(FacturaVentaSerializer):
    paciente = PacienteListSerializer(read_only=True)
    obra_social = ObraSocialSerializer(read_only=True)
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    pagos = PagoSerializer(many=True, read_only=True)

    class Meta(FacturaVentaSerializer.Meta):
        fields = FacturaVentaSerializer.Meta.fields + ['paciente', 'obra_social', 'detalles', 'pagos']