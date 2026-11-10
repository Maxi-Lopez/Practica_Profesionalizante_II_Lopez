import pytest
from decimal import Decimal
from model_bakery import baker


@pytest.mark.django_db
class TestFacturaVentaModel:
    """Tests de lógica de negocio del modelo FacturaVenta."""

    def setup_method(self):
        """Configuración común para los tests."""
        from personas.models import Persona, Pais, Provincia, Localidad
        from pacientes.models import Paciente, ObraSocial
        from servicios.models import Servicio, TipoServicio

        self.pais = baker.make(Pais, nombre="Argentina")
        self.provincia = baker.make(Provincia, nombre="Córdoba", pais=self.pais)
        self.localidad = baker.make(Localidad, nombre="Río Cuarto", provincia=self.provincia)

        self.persona = baker.make(
            Persona, nombre="Juan", apellido="Pérez", dni="12345678", localidad=self.localidad
        )
        self.paciente = baker.make(Paciente, persona=self.persona)
        self.obra_social = baker.make(ObraSocial, nombre="OSDE")

        self.tipo_servicio = baker.make(TipoServicio, nombre="Consulta")
        self.servicio = baker.make(Servicio, tipo_servicio=self.tipo_servicio, nombre="Consulta general")

    def test_total_factura_sin_descuento_calcula_correctamente(self):
        """
        Test 4a: Verificar que total = suma(detalles.subtotal) cuando no hay descuento.
        Arrange: Crear FacturaVenta con 1 detalle (cantidad=2, precio_unitario=1000).
        Act: Llamar a calcular_total().
        Assert: total = 2000, subtotal = 2000.
        """
        factura = baker.make(
            "facturacion.FacturaVenta",
            paciente=self.paciente,
            obra_social=self.obra_social,
            numero_factura="F-001",
            descuento=Decimal("0"),
        )

        baker.make(
            "facturacion.DetalleVenta",
            factura=factura,
            servicio=self.servicio,
            descripcion="Consulta general",
            cantidad=2,
            precio_unitario=Decimal("1000"),
            subtotal=Decimal("2000"),
        )

        total = factura.calcular_total()

        assert factura.subtotal == Decimal("2000")
        assert factura.total == Decimal("2000")
        assert total == Decimal("2000")

    def test_total_factura_con_descuento_calcula_correctamente(self):
        """
        Test 4b: Verificar que total = suma(detalles.subtotal) - descuento.
        Arrange: Crear FacturaVenta con descuento=100, 1 detalle (cantidad=2, precio=1000).
        Act: Llamar a calcular_total().
        Assert: total = 1900 (2000 - 100).
        """
        factura = baker.make(
            "facturacion.FacturaVenta",
            paciente=self.paciente,
            obra_social=self.obra_social,
            numero_factura="F-002",
            descuento=Decimal("100"),
        )

        baker.make(
            "facturacion.DetalleVenta",
            factura=factura,
            servicio=self.servicio,
            descripcion="Consulta general",
            cantidad=2,
            precio_unitario=Decimal("1000"),
            subtotal=Decimal("2000"),
        )

        total = factura.calcular_total()

        assert factura.subtotal == Decimal("2000")
        assert factura.total == Decimal("1900")
        assert total == Decimal("1900")

    def test_total_factura_multiples_detalles_calcula_correctamente(self):
        """
        Verificar cálculo con múltiples detalles y descuento.
        """
        factura = baker.make(
            "facturacion.FacturaVenta",
            paciente=self.paciente,
            obra_social=self.obra_social,
            numero_factura="F-003",
            descuento=Decimal("50"),
        )

        # Detalle 1: 2 x 1000 = 2000
        baker.make(
            "facturacion.DetalleVenta",
            factura=factura,
            servicio=self.servicio,
            descripcion="Consulta",
            cantidad=2,
            precio_unitario=Decimal("1000"),
            subtotal=Decimal("2000"),
        )

        # Detalle 2: 1 x 1500 = 1500
        baker.make(
            "facturacion.DetalleVenta",
            factura=factura,
            servicio=self.servicio,
            descripcion="Sesión extendida",
            cantidad=1,
            precio_unitario=Decimal("1500"),
            subtotal=Decimal("1500"),
        )

        total = factura.calcular_total()

        assert factura.subtotal == Decimal("3500")  # 2000 + 1500
        assert factura.total == Decimal("3450")      # 3500 - 50
        assert total == Decimal("3450")

    def test_calcular_total_sin_detalles_devuelve_cero(self):
        """
        Verificar que calcular_total() devuelve 0 si no hay detalles.
        """
        factura = baker.make(
            "facturacion.FacturaVenta",
            paciente=self.paciente,
            numero_factura="F-004",
        )

        total = factura.calcular_total()

        assert factura.subtotal == Decimal("0")
        assert factura.total == Decimal("0")
        assert total == Decimal("0")