from rest_framework import serializers
from .models import Proveedor, Compra, DetalleCompra, TipoGasto, Gasto
from inventario.serializers import ProductoListSerializer


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = [
            'id',
            'razon_social',
            'cuit',
            'telefono',
            'email',
            'direccion',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'activo']

    def validate_cuit(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("El CUIT debe contener solo números.")
        if len(value) != 11:
            raise serializers.ValidationError("El CUIT debe tener 11 dígitos.")
        return value

    def validate_email(self, value):
        if value and '@' not in value:
            raise serializers.ValidationError("El email no es válido.")
        return value


class ProveedorGetSerializer(ProveedorSerializer):
    class Meta(ProveedorSerializer.Meta):
        fields = ProveedorSerializer.Meta.fields


class ProveedorPostSerializer(ProveedorSerializer):
    class Meta(ProveedorSerializer.Meta):
        fields = ['razon_social', 'cuit', 'telefono', 'email', 'direccion']


class DetalleCompraSerializer(serializers.ModelSerializer):
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductoListSerializer.Meta.model.objects.all(),
        source='producto',
        write_only=True,
        required=False,
    )

    class Meta:
        model = DetalleCompra
        fields = [
            'id',
            'compra',
            'producto',
            'producto_id',
            'cantidad',
            'precio_unitario',
            'subtotal',
        ]
        read_only_fields = ['id', 'subtotal']

    def validate(self, attrs):
        cantidad = attrs.get('cantidad', 1)
        precio_unitario = attrs.get('precio_unitario')
        if precio_unitario is not None:
            attrs['subtotal'] = cantidad * precio_unitario
        return attrs


class DetalleCompraGetSerializer(DetalleCompraSerializer):
    producto = ProductoListSerializer(read_only=True)

    class Meta(DetalleCompraSerializer.Meta):
        fields = DetalleCompraSerializer.Meta.fields + ['producto']


class DetalleCompraPostSerializer(DetalleCompraSerializer):
    class Meta(DetalleCompraSerializer.Meta):
        fields = ['compra', 'producto_id', 'cantidad', 'precio_unitario']


class CompraSerializer(serializers.ModelSerializer):
    proveedor_id = serializers.PrimaryKeyRelatedField(
        queryset=Proveedor.objects.all(),
        source='proveedor',
        write_only=True,
        required=False,
    )

    class Meta:
        model = Compra
        fields = [
            'id',
            'proveedor',
            'proveedor_id',
            'fecha',
            'numero_comprobante',
            'total',
            'observaciones',
            'anulada',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha', 'fecha_actualizacion', 'total', 'anulada']

    def validate(self, attrs):
        from django.utils import timezone

        fecha = attrs.get('fecha')
        if fecha and fecha > timezone.now():
            raise serializers.ValidationError({
                'fecha': 'La fecha no puede ser futura.'
            })

        return attrs


class CompraGetSerializer(CompraSerializer):
    proveedor = ProveedorGetSerializer(read_only=True)
    detalles = DetalleCompraGetSerializer(many=True, read_only=True)

    class Meta(CompraSerializer.Meta):
        fields = CompraSerializer.Meta.fields + ['proveedor', 'detalles']


class CompraPostSerializer(CompraSerializer):
    class Meta(CompraSerializer.Meta):
        fields = ['proveedor_id', 'fecha', 'numero_comprobante', 'observaciones']


class TipoGastoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoGasto
        fields = ['id', 'nombre', 'descripcion', 'activo']
        read_only_fields = ['id', 'activo']


class TipoGastoGetSerializer(TipoGastoSerializer):
    class Meta(TipoGastoSerializer.Meta):
        fields = TipoGastoSerializer.Meta.fields


class TipoGastoPostSerializer(TipoGastoSerializer):
    class Meta(TipoGastoSerializer.Meta):
        fields = ['nombre', 'descripcion']


class GastoSerializer(serializers.ModelSerializer):
    tipo_gasto_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoGasto.objects.all(),
        source='tipo_gasto',
        write_only=True,
        required=False,
    )
    proveedor_id = serializers.PrimaryKeyRelatedField(
        queryset=Proveedor.objects.all(),
        source='proveedor',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Gasto
        fields = [
            'id',
            'tipo_gasto',
            'tipo_gasto_id',
            'proveedor',
            'proveedor_id',
            'fecha',
            'concepto',
            'monto',
            'numero_comprobante',
            'observaciones',
            'anulado',
            'fecha_creacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'anulado']

    def validate_monto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a cero.")
        return value


class GastoGetSerializer(GastoSerializer):
    tipo_gasto = TipoGastoGetSerializer(read_only=True)
    proveedor = ProveedorGetSerializer(read_only=True)

    class Meta(GastoSerializer.Meta):
        fields = GastoSerializer.Meta.fields + ['tipo_gasto', 'proveedor']


class GastoPostSerializer(GastoSerializer):
    class Meta(GastoSerializer.Meta):
        fields = ['tipo_gasto_id', 'proveedor_id', 'fecha', 'concepto', 'monto', 'numero_comprobante', 'observaciones']