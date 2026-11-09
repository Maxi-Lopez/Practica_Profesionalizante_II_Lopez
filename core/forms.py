from django import forms
from pacientes.models import Paciente, ObraSocial
from personas.models import Persona, Localidad


class PacienteForm(forms.ModelForm):
    # Persona fields
    nombre = forms.CharField(
        max_length=150,
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    apellido = forms.CharField(
        max_length=150,
        label="Apellido",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    dni = forms.CharField(
        max_length=30,
        label="DNI",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    fecha_nacimiento = forms.DateField(
        required=False,
        label="Fecha de Nacimiento",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    direccion = forms.CharField(
        max_length=255,
        required=False,
        label="Dirección",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    localidad = forms.ModelChoiceField(
        queryset=Localidad.objects.filter(activo=True),
        required=False,
        label="Localidad",
        empty_label="Seleccionar localidad",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    telefono = forms.CharField(
        max_length=50,
        required=False,
        label="Teléfono",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    email = forms.EmailField(
        required=False,
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )

    # Paciente fields
    obra_social = forms.ModelChoiceField(
        queryset=ObraSocial.objects.filter(activo=True),
        required=False,
        label="Obra Social",
        empty_label="Seleccionar obra social",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    nro_afiliado = forms.CharField(
        max_length=100,
        required=False,
        label="Número de Afiliado",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    numero_cud = forms.CharField(
        max_length=100,
        required=False,
        label="Número CUD",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    fecha_vencimiento_cud = forms.DateField(
        required=False,
        label="Vencimiento CUD",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    fecha_ingreso = forms.DateField(
        required=False,
        label="Fecha de Ingreso",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    historia_clinica = forms.CharField(
        max_length=80,
        required=False,
        label="Historia Clínica",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )

    class Meta:
        model = Paciente
        fields = [
            'obra_social', 'nro_afiliado', 'numero_cud', 'fecha_vencimiento_cud',
            'fecha_ingreso', 'historia_clinica'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.persona:
            persona = self.instance.persona
            self.fields['nombre'].initial = persona.nombre
            self.fields['apellido'].initial = persona.apellido
            self.fields['dni'].initial = persona.dni
            self.fields['fecha_nacimiento'].initial = persona.fecha_nacimiento
            self.fields['direccion'].initial = persona.direccion
            self.fields['localidad'].initial = persona.localidad
            # Get first phone
            telefono = persona.telefonos.first()
            if telefono:
                self.fields['telefono'].initial = telefono.numero
            # Get first email
            email = persona.emails.first()
            if email:
                self.fields['email'].initial = email.direccion_email

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio.")
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        # Verificar que no sea solo símbolos
        if not any(c.isalpha() for c in nombre):
            raise forms.ValidationError("El nombre debe contener al menos una letra.")
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido', '').strip()
        if not apellido:
            raise forms.ValidationError("El apellido es obligatorio.")
        if len(apellido) < 2:
            raise forms.ValidationError("El apellido debe tener al menos 2 caracteres.")
        if not any(c.isalpha() for c in apellido):
            raise forms.ValidationError("El apellido debe contener al menos una letra.")
        return apellido

    def clean_dni(self):
        dni = self.cleaned_data.get('dni', '').strip()
        if not dni:
            raise forms.ValidationError("El DNI es obligatorio.")
        if not dni.isdigit():
            raise forms.ValidationError("El DNI debe contener solo números.")
        if len(dni) < 7:
            raise forms.ValidationError("El DNI debe tener al menos 7 dígitos.")
        if len(dni) > 10:
            raise forms.ValidationError("El DNI no puede tener más de 10 dígitos.")
        
        # Verificar duplicado (excluyendo la instancia actual en edición)
        from personas.models import Persona
        qs = Persona.objects.filter(dni=dni)
        if self.instance and self.instance.pk and self.instance.persona:
            qs = qs.exclude(pk=self.instance.persona.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe una persona con este DNI.")
        return dni

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if fecha:
            from django.utils import timezone
            if fecha > timezone.now().date():
                raise forms.ValidationError("La fecha de nacimiento no puede ser futura.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        dni = cleaned_data.get('dni')
        if dni:
            # Validación adicional de DNI único a nivel de formulario
            from personas.models import Persona
            qs = Persona.objects.filter(dni=dni)
            if self.instance and self.instance.pk and self.instance.persona:
                qs = qs.exclude(pk=self.instance.persona.pk)
            if qs.exists():
                self.add_error('dni', "Ya existe una persona con este DNI.")

        # Validación cruzada: Obra Social → Nro. Afiliado
        obra_social = cleaned_data.get('obra_social')
        nro_afiliado = cleaned_data.get('nro_afiliado')
        if obra_social and not nro_afiliado:
            self.add_error('nro_afiliado', "Si el paciente tiene obra social, el número de afiliado es obligatorio.")

        # Validación condicional CUD: numero_cud → fecha_vencimiento_cud
        numero_cud = cleaned_data.get('numero_cud')
        fecha_vencimiento_cud = cleaned_data.get('fecha_vencimiento_cud')
        if numero_cud and not fecha_vencimiento_cud:
            self.add_error('fecha_vencimiento_cud', "Si el paciente tiene CUD, debe indicar la fecha de vencimiento.")

        # Validar que fecha_vencimiento_cud no sea pasada
        if fecha_vencimiento_cud:
            from django.utils import timezone
            if fecha_vencimiento_cud < timezone.now().date():
                self.add_error('fecha_vencimiento_cud', "La fecha de vencimiento del CUD no puede ser una fecha pasada.")

        return cleaned_data

    def save(self, commit=True):
        paciente = super().save(commit=False)
        
        # Create or update Persona
        if self.instance and self.instance.pk and self.instance.persona:
            persona = self.instance.persona
        else:
            persona = Persona()
        
        persona.nombre = self.cleaned_data['nombre']
        persona.apellido = self.cleaned_data['apellido']
        persona.dni = self.cleaned_data['dni']
        persona.fecha_nacimiento = self.cleaned_data['fecha_nacimiento']
        persona.direccion = self.cleaned_data['direccion']
        persona.localidad = self.cleaned_data['localidad']
        persona.activo = True
        
        if commit:
            persona.save()
            
            # Update phone
            telefono_numero = self.cleaned_data.get('telefono')
            if telefono_numero:
                from personas.models import Telefono
                telefono, _ = Telefono.objects.get_or_create(persona=persona, defaults={'tipo': 'CELULAR', 'es_principal': True})
                telefono.numero = telefono_numero
                telefono.save()
            
            # Update email
            email_direccion = self.cleaned_data.get('email')
            if email_direccion:
                from personas.models import Email
                email, _ = Email.objects.get_or_create(persona=persona, defaults={'tipo': 'PERSONAL', 'es_principal': True})
                email.direccion_email = email_direccion
                email.save()
            
            paciente.persona = persona
            paciente.save()
        
        return paciente