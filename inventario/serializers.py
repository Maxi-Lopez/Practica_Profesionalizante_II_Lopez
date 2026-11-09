from rest_framework import serializers
from .models import CategoriaProducto, Producto, MovimientoStock


class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = ['id', 'nombre', 'descripcion', 'activo']
        read_only_fields = ['id', 'activo']


class ProductoSerializer(serializers.ModelSerializer):
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaProducto.objects.all(),
        source='categoria',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Producto
        fields = [
            'id',
            'categoria',
            'categoria_id',
            'nombre',
            'descripcion',
            'codigo',
            'stock_actual',
            'stock_minimo',
            'precio_compra',
            'precio_venta',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'activo', 'stock_actual']


class ProductoListSerializer(ProductoSerializer):
    categoria = CategoriaProductoSerializer(read_only=True)

    class Meta(ProductoSerializer.Meta):
        fields = ProductoSerializer.Meta.fields + ['categoria']


class MovimientoStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoStock
        fields = [
            'id',
            'producto',
            'tipo',
            'cantidad',
            'stock_anterior',
            'stock_resultante',
            'motivo',
            'fecha',
        ]
        read_only_fields = ['id', 'fecha', 'stock_resultante']

    def validate(self, attrs):
        tipo = attrs.get('tipo')
        cantidad = attrs.get('cantidad')
        stock_anterior = attrs.get('stock_anterior')

        if tipo and cantidad is not None and stock_anterior is not None:
            if tipo == MovimientoStock.TipoMovimiento.ENTRADA:
                stock_resultante = stock_anterior + cantidad
            elif tipo == MovimientoStock.TipoMovimiento.SALIDA:
                stock_resultante = stock_anterior - cantidad
                if stock_resultante < 0:
                    raise serializers.ValidationError({
                        'cantidad': 'No hay stock suficiente para realizar esta salida.'
                    })
            elif tipo == MovimientoStock.TipoMovimiento.AJUSTE:
                stock_resultante = cantidad
            else:
                raise serializers.ValidationError({
                    'tipo': 'Tipo de movimiento inválido.'
                })

            attrs['stock_resultante'] = stock_resultante

        return attrs


class MovimientoStockListSerializer(MovimientoStockSerializer):
    producto = ProductoListSerializer(read_only=True)

    class Meta(MovimientoStockSerializer.Meta):
        fields = MovimientoStockSerializer.Meta.fields + ['producto']