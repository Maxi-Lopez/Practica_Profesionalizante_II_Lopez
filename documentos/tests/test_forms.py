import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from model_bakery import baker
from decimal import Decimal


@pytest.mark.django_db
class TestDocumentoForm:
    """Tests de validación del formulario DocumentoForm."""

    def setup_method(self):
        """Configuración común para los tests."""
        from personas.models import Persona, Pais, Provincia, Localidad
        
        self.pais = baker.make(Pais, nombre="Argentina")
        self.provincia = baker.make(Provincia, nombre="Córdoba", pais=self.pais)
        self.localidad = baker.make(Localidad, nombre="Río Cuarto", provincia=self.provincia)
        
        self.persona = baker.make(
            Persona, nombre="Juan", apellido="Pérez", dni="12345678", localidad=self.localidad
        )

    def test_form_valida_con_archivo_pdf(self):
        """
        Test: Formulario válido con archivo PDF válido.
        """
        from core.forms import DocumentoForm
        
        pdf_content = b"%PDF-1.4 test content"
        pdf_file = SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")
        
        data = {
            'persona': self.persona.pk,
            'tipo': 'DNI',
            'nombre': 'Documento de prueba',
            'descripcion': 'Descripción de prueba',
            'fecha_documento': '2024-01-15',
            'fecha_vencimiento': '2025-01-15',
        }
        form = DocumentoForm(data=data, files={'archivo': pdf_file})
        
        assert form.is_valid(), f"Errores: {form.errors}"

    def test_form_valida_con_archivo_jpg(self):
        """
        Test: Formulario válido con archivo JPG válido.
        """
        from core.forms import DocumentoForm
        
        jpg_content = b"\xff\xd8\xff\xe0\x00\x10JFIF"  # JPEG header
        jpg_file = SimpleUploadedFile("test.jpg", jpg_content, content_type="image/jpeg")
        
        data = {
            'persona': self.persona.pk,
            'tipo': 'DNI',
            'nombre': 'Foto DNI',
            'fecha_documento': '2024-01-15',
        }
        form = DocumentoForm(data=data, files={'archivo': jpg_file})
        
        assert form.is_valid(), f"Errores: {form.errors}"

    def test_form_rechaza_extension_invalida(self):
        """
        Test: Formulario rechaza archivo con extensión no permitida.
        """
        from core.forms import DocumentoForm
        
        txt_content = b"texto plano"
        txt_file = SimpleUploadedFile("test.txt", txt_content, content_type="text/plain")
        
        data = {
            'persona': self.persona.pk,
            'tipo': 'OTRO',
            'nombre': 'Archivo inválido',
            'fecha_documento': '2024-01-15',
        }
        form = DocumentoForm(data=data, files={'archivo': txt_file})
        
        assert not form.is_valid()
        assert 'archivo' in form.errors
        assert "Extensión de archivo no permitida" in str(form.errors['archivo'])

    def test_form_rechaza_archivo_muy_grande(self):
        """
        Test: Formulario rechaza archivo mayor a 10 MB.
        """
        from core.forms import DocumentoForm
        
        # Crear archivo de 11 MB
        large_content = b"x" * (11 * 1024 * 1024)
        large_file = SimpleUploadedFile("grande.pdf", large_content, content_type="application/pdf")
        
        data = {
            'persona': self.persona.pk,
            'tipo': 'OTRO',
            'nombre': 'Archivo grande',
            'fecha_documento': '2024-01-15',
        }
        form = DocumentoForm(data=data, files={'archivo': large_file})
        
        assert not form.is_valid()
        assert 'archivo' in form.errors
        assert "supera el tamaño máximo" in str(form.errors['archivo'])

    def test_form_rechaza_fecha_vencimiento_anterior(self):
        """
        Test: Formulario rechaza fecha_vencimiento anterior a fecha_documento.
        """
        from core.forms import DocumentoForm
        
        pdf_content = b"%PDF-1.4 test"
        pdf_file = SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")
        
        data = {
            'persona': self.persona.pk,
            'tipo': 'DNI',
            'nombre': 'Documento',
            'fecha_documento': '2024-01-20',
            'fecha_vencimiento': '2024-01-10',  # Anterior a fecha_documento
        }
        form = DocumentoForm(data=data, files={'archivo': pdf_file})
        
        assert not form.is_valid()
        assert 'fecha_vencimiento' in form.errors
        assert "posterior" in str(form.errors['fecha_vencimiento'])

    def test_form_acepta_fecha_vencimiento_posterior(self):
        """
        Test: Formulario acepta fecha_vencimiento posterior a fecha_documento.
        """
        from core.forms import DocumentoForm
        
        pdf_content = b"%PDF-1.4 test"
        pdf_file = SimpleUploadedFile("test.pdf", b"%PDF-1.4 test", content_type="application/pdf")
        
        data = {
            'persona': self.persona.pk,
            'tipo': 'DNI',
            'nombre': 'Documento',
            'fecha_documento': '2024-01-10',
            'fecha_vencimiento': '2024-02-10',  # Posterior
        }
        form = DocumentoForm(data=data, files={'archivo': pdf_file})
        
        assert form.is_valid(), f"Errores: {form.errors}"

    def test_form_queryset_persona_filtrado_activo(self):
        """
        Test: El queryset de persona está filtrado por activo=True.
        """
        from core.forms import DocumentoForm
        from personas.models import Persona
        
        persona_activa = baker.make(Persona, nombre="Activo", apellido="User", dni="11111111")
        persona_inactiva = baker.make(Persona, nombre="Inactivo", apellido="User", dni="22222222", activo=False)
        
        form = DocumentoForm()
        qs = form.fields['persona'].queryset
        
        assert persona_activa in qs
        assert persona_inactiva not in qs
        # Verificar ordenamiento
        nombres = list(qs.values_list('apellido', 'nombre'))
        assert nombres == sorted(nombres)