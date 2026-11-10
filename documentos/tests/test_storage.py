import pytest
from django.core.files.storage import FileSystemStorage


@pytest.mark.django_db
class TestDocumentoStorage:
    """Tests de configuración de storage para Documento."""

    def test_storage_default_es_filesystem_cuando_use_supabase_false(self):
        """
        Test: Con USE_SUPABASE_STORAGE=False, el campo archivo usa FileSystemStorage.
        """
        from documentos.models import Documento
        
        storage = Documento._meta.get_field('archivo').storage
        
        assert isinstance(storage, FileSystemStorage)

    def test_storage_ruta_media_root_correcta(self):
        """
        Test: FileSystemStorage usa MEDIA_ROOT correcto.
        """
        from django.conf import settings
        from documentos.models import Documento
        
        storage = Documento._meta.get_field('archivo').storage
        
        assert str(storage.location) == str(settings.MEDIA_ROOT)
        assert storage.base_url == '/media/'