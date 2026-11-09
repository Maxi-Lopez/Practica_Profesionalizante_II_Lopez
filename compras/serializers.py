from rest_framework import serializers
from .models import Proveedor, Compra, DetalleCompra, TipoGasto, Gasto


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


class TipoGastoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoGasto
        fields = ['id', 'nombre', 'descripcion', 'activo']
        read_only_fields = ['id', 'activo']


class DetalleCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleCompra
        fields = [
            'id',
            'compra',
            'producto',
            'cantidad',
            'precio_unitario',
            'subtotal',
        ]
        read_only_fields = ['id', 'subtotal']

    def validate(self, attrs):
        cantidad = attrs.get('cantidad')
        precio_unitario = attrs.get('precio_unitario')

        if cantidad is not None and precio_unitario is not None:
            attrs['subtotal'] = cantidad * precio_unitario

        return attrs


class DetalleCompraListSerializer(DetalleCompraSerializer):
    producto = serializers.SerializerMethodField()

    class Meta(DetalleCompraSerializer.Meta):
        fields = DetalleCompraSerializer.Meta.fields + ['producto']

    def get_producto(self, obj):
        return {
            'id': obj.producto.id,
            'nombre': obj.producto.nombre,
            'codigo': obj.producto.codigo,
        }


class GastoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gasto
        fields = [
            'id',
            'tipo_gasto',
            'proveedor',
            'fecha',
            'concepto',
            'monto',
            'numero_comprobante',
            'observaciones',
            'anulado',
            'fecha_creacion',
        ]
        read_only_fields = ['id', 'fecha_creacion']


class GastoListSerializer(GastoSerializer):
    tipo_gasto = TipoGastoSerializer(read_only=True)
    proveedor = ProveedorSerializer(read_only=True)

    class Meta(GastoSerializer.Meta):
        fields = GastoSerializer.Meta.fields + ['tipo_gasto', 'proveedor']


class CompraSerializer(serializers.ModelSerializer):
    detalles = DetalleCompraSerializer(many=True, required=False)
    gastos = GastoSerializer(many=True, required=False)

    class Meta:
        model = Compra
        fields = [
            'id',
            'proveedor',
            'fecha',
            'numero_comprobante',
            'total',
            'observaciones',
            'anulada',
            'fecha_actualizacion',
            'detalles',
            'gastos',
        ]
        read_only_fields = ['id', 'fecha', 'fecha_actualizacion']

    def validate(self, attrs):
        detalles = attrs.get('detalles', [])
        total = attrs.get('total', 0)

        if detalles:
            total_detalles = sum(d.get('subtotal', 0) for d in detalles)
            if total_detalles != total:
                raise serializers.ValidationError({
                    'total': f'El total ({total}) debe ser igual a la suma de los subtotales de los detalles ({total_detalles}).'
                })

        return attrs


class CompraListSerializer(CompraSerializer):
    proveedor = ProveedorSerializer(read_only=True)
    detalles = DetalleCompraListSerializer(many=True, read_only=True)
    gastos = GastoListSerializer(many=True, read_only=True)

    class Meta(CompraSerializer.Meta):
        fields = CompraSerializer.Meta.fields + ['proveedor', 'detalles', 'gastos']