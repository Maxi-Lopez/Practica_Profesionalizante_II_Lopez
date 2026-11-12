from django import forms
from pacientes.models import (
    Paciente, ObraSocial, Sala, AreaInterdisciplinaria, 
    DiagnosticoArea, SeguimientoTrimestral
)
from empleados.models import Empleado, Rol
from documentos.models import Documento
from personas.models import Persona, Localidad
from compras.models import Proveedor, Compra, DetalleCompra, TipoGasto, Gasto
from inventario.models import Producto
from tratamientos.models import (
    PlanTratamiento, ObjetivoTratamiento, ActividadPlan,
    HistorialMedico, EvolucionSemanal, RegistroActividad, NotaImportante
)
from servicios.models import Servicio
from turnos.models import Turno, EstadoTurno


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
    foto = forms.ImageField(
        required=False,
        label="Foto de perfil",
        widget=forms.ClearableFileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
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
            
            # Update foto
            foto = self.cleaned_data.get('foto')
            if foto:
                persona.foto = foto
                persona.save()
            
            paciente.persona = persona
            paciente.save()
        
        return paciente


class EmpleadoForm(forms.ModelForm):
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
    foto = forms.ImageField(
        required=False,
        label="Foto de perfil",
        widget=forms.ClearableFileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )

    # Empleado fields
    matricula = forms.CharField(
        max_length=50,
        required=False,
        label="Matrícula",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    fecha_ingreso = forms.DateField(
        required=False,
        label="Fecha de Ingreso",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    horas_semanales = forms.IntegerField(
        required=False,
        label="Horas Semanales",
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    roles = forms.ModelMultipleChoiceField(
        queryset=Rol.objects.filter(activo=True),
        required=False,
        label="Roles",
        widget=forms.SelectMultiple(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )

    class Meta:
        model = Empleado
        fields = [
            'matricula', 'fecha_ingreso', 'horas_semanales', 'roles'
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
            # Get current roles
            self.fields['roles'].initial = self.instance.roles.filter(activo=True).values_list('rol', flat=True)

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio.")
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
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

    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula', '').strip()
        if matricula:
            from empleados.models import Empleado
            qs = Empleado.objects.filter(matricula=matricula)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Ya existe un empleado con esta matrícula.")
        return matricula

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
        
        matricula = cleaned_data.get('matricula')
        if matricula:
            from empleados.models import Empleado
            qs = Empleado.objects.filter(matricula=matricula)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('matricula', "Ya existe un empleado con esta matrícula.")

        return cleaned_data

    def save(self, commit=True):
        empleado = super().save(commit=False)
        
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
            
            # Update foto
            foto = self.cleaned_data.get('foto')
            if foto:
                persona.foto = foto
                persona.save()
            
            empleado.persona = persona
            empleado.save()
            
            # Update roles
            roles = self.cleaned_data.get('roles')
            if roles is not None:
                from empleados.models import EmpleadoRol
                # Desactivar roles existentes no en la nueva lista
                EmpleadoRol.objects.filter(empleado=empleado).exclude(rol__in=roles).update(activo=False)
                # Crear o activar roles seleccionados
                for rol in roles:
                    EmpleadoRol.objects.update_or_create(
                        empleado=empleado,
                        rol=rol,
                        defaults={'activo': True}
                    )
        
        return empleado


class SalaForm(forms.ModelForm):
    nombre = forms.CharField(
        max_length=100,
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    orientador = forms.ModelChoiceField(
        queryset=Empleado.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre'),
        required=False,
        label="Orientador",
        empty_label="Seleccionar orientador",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    planificacion_actividades = forms.CharField(
        required=False,
        label="Planificación de Actividades",
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'rows': 4})
    )

    class Meta:
        model = Sala
        fields = ['nombre', 'orientador', 'planificacion_actividades']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['orientador'].queryset = Empleado.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre')


class AreaInterdisciplinariaForm(forms.ModelForm):
    nombre = forms.ChoiceField(
        choices=AreaInterdisciplinaria.NombreArea.choices,
        label="Nombre",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    descripcion = forms.CharField(
        required=False,
        label="Descripción",
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'rows': 4})
    )

    class Meta:
        model = AreaInterdisciplinaria
        fields = ['nombre', 'descripcion']


class DiagnosticoAreaForm(forms.ModelForm):
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre'),
        label="Paciente",
        empty_label="Seleccionar paciente",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    area = forms.ModelChoiceField(
        queryset=AreaInterdisciplinaria.objects.filter(activo=True).order_by('nombre'),
        label="Área",
        empty_label="Seleccionar área",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    fecha = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    diagnostico = forms.CharField(
        label="Diagnóstico",
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'rows': 4})
    )
    profesional = forms.ModelChoiceField(
        queryset=Empleado.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre'),
        required=False,
        label="Profesional",
        empty_label="Seleccionar profesional",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )

    class Meta:
        model = DiagnosticoArea
        fields = ['paciente', 'area', 'fecha', 'diagnostico', 'profesional']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paciente'].queryset = Paciente.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre')
        self.fields['area'].queryset = AreaInterdisciplinaria.objects.filter(activo=True).order_by('nombre')
        self.fields['profesional'].queryset = Empleado.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre')


class SeguimientoTrimestralForm(forms.ModelForm):
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre'),
        label="Paciente",
        empty_label="Seleccionar paciente",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    area = forms.ModelChoiceField(
        queryset=AreaInterdisciplinaria.objects.filter(activo=True).order_by('nombre'),
        label="Área",
        empty_label="Seleccionar área",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    fecha = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    observaciones = forms.CharField(
        label="Observaciones",
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'rows': 4})
    )
    profesional = forms.ModelChoiceField(
        queryset=Empleado.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre'),
        required=False,
        label="Profesional",
        empty_label="Seleccionar profesional",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    es_intervencion_mensual = forms.BooleanField(
        required=False,
        label="Intervención Mensual",
        help_text="Marcar si es una intervención mensual (algunas áreas lo requieren)",
        widget=forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-2 focus:ring-primary-500'})
    )

    class Meta:
        model = SeguimientoTrimestral
        fields = ['paciente', 'area', 'fecha', 'observaciones', 'profesional', 'es_intervencion_mensual']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paciente'].queryset = Paciente.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre')
        self.fields['area'].queryset = AreaInterdisciplinaria.objects.filter(activo=True).order_by('nombre')
        self.fields['profesional'].queryset = Empleado.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre')


class DocumentoForm(forms.ModelForm):
    persona = forms.ModelChoiceField(
        queryset=Persona.objects.filter(activo=True).order_by('apellido', 'nombre'),
        label="Persona",
        empty_label="Seleccionar persona",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    tipo = forms.ChoiceField(
        choices=Documento.TipoDocumento.choices,
        label="Tipo",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    nombre = forms.CharField(
        max_length=200,
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    archivo = forms.FileField(
        label="Archivo",
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    descripcion = forms.CharField(
        required=False,
        label="Descripción",
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'rows': 4})
    )
    fecha_documento = forms.DateField(
        required=False,
        label="Fecha del Documento",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    fecha_vencimiento = forms.DateField(
        required=False,
        label="Fecha de Vencimiento",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )

    class Meta:
        model = Documento
        fields = ['persona', 'tipo', 'nombre', 'archivo', 'descripcion', 'fecha_documento', 'fecha_vencimiento']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['persona'].queryset = Persona.objects.filter(activo=True).order_by('apellido', 'nombre')

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            # Validar extensión
            ext = archivo.name.lower().rsplit('.', 1)[-1] if '.' in archivo.name else ''
            extensiones_permitidas = ['pdf', 'jpg', 'jpeg', 'png']
            if ext not in extensiones_permitidas:
                raise forms.ValidationError("Extensión de archivo no permitida. Solo se permiten: .pdf, .jpg, .jpeg, .png")
            
            # Validar tamaño (10 MB = 10 * 1024 * 1024 bytes)
            max_size = 10 * 1024 * 1024
            if archivo.size > max_size:
                raise forms.ValidationError("El archivo supera el tamaño máximo permitido de 10 MB.")
        return archivo

    def clean(self):
        cleaned_data = super().clean()
        fecha_documento = cleaned_data.get('fecha_documento')
        fecha_vencimiento = cleaned_data.get('fecha_vencimiento')
        
        if fecha_vencimiento and fecha_documento and fecha_vencimiento <= fecha_documento:
            self.add_error('fecha_vencimiento', "La fecha de vencimiento debe ser posterior a la fecha del documento.")
        
        return cleaned_data


class ProveedorForm(forms.ModelForm):
    razon_social = forms.CharField(
        max_length=150,
        label="Razón Social",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    cuit = forms.CharField(
        max_length=20,
        label="CUIT",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
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
    direccion = forms.CharField(
        max_length=255,
        required=False,
        label="Dirección",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )

    class Meta:
        model = Proveedor
        fields = ['razon_social', 'cuit', 'telefono', 'email', 'direccion']

    def clean_cuit(self):
        cuit = self.cleaned_data.get('cuit', '').strip()
        if not cuit:
            raise forms.ValidationError("El CUIT es obligatorio.")
        if not cuit.isdigit():
            raise forms.ValidationError("El CUIT debe contener solo números.")
        if len(cuit) != 11:
            raise forms.ValidationError("El CUIT debe tener 11 dígitos.")
        
        qs = Proveedor.objects.filter(cuit=cuit)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un proveedor con este CUIT.")
        return cuit

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if email and '@' not in email:
            raise forms.ValidationError("El email no es válido.")
        return email


class TipoGastoForm(forms.ModelForm):
    nombre = forms.CharField(
        max_length=100,
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    descripcion = forms.CharField(
        max_length=255,
        required=False,
        label="Descripción",
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'rows': 3})
    )

    class Meta:
        model = TipoGasto
        fields = ['nombre', 'descripcion']

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio.")
        
        qs = TipoGasto.objects.filter(nombre__iexact=nombre)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un tipo de gasto con este nombre.")
        return nombre


class CompraForm(forms.ModelForm):
    proveedor = forms.ModelChoiceField(
        queryset=Proveedor.objects.filter(activo=True).order_by('razon_social'),
        label="Proveedor",
        empty_label="Seleccionar proveedor",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    numero_comprobante = forms.CharField(
        max_length=100,
        required=False,
        label="Número de Comprobante",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    observaciones = forms.CharField(
        required=False,
        label="Observaciones",
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'rows': 3})
    )

    class Meta:
        model = Compra
        fields = ['proveedor', 'numero_comprobante', 'observaciones']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proveedor'].queryset = Proveedor.objects.filter(activo=True).order_by('razon_social')


class GastoForm(forms.ModelForm):
    tipo_gasto = forms.ModelChoiceField(
        queryset=TipoGasto.objects.filter(activo=True).order_by('nombre'),
        label="Tipo de Gasto",
        empty_label="Seleccionar tipo de gasto",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    proveedor = forms.ModelChoiceField(
        queryset=Proveedor.objects.filter(activo=True).order_by('razon_social'),
        required=False,
        label="Proveedor",
        empty_label="Seleccionar proveedor (opcional)",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    fecha = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    concepto = forms.CharField(
        max_length=255,
        label="Concepto",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    monto = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        label="Monto",
        widget=forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'step': '0.01', 'min': '0.01'})
    )
    numero_comprobante = forms.CharField(
        max_length=100,
        required=False,
        label="Número de Comprobante",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    observaciones = forms.CharField(
        required=False,
        label="Observaciones",
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'rows': 3})
    )

    class Meta:
        model = Gasto
        fields = ['tipo_gasto', 'proveedor', 'fecha', 'concepto', 'monto', 'numero_comprobante', 'observaciones']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_gasto'].queryset = TipoGasto.objects.filter(activo=True).order_by('nombre')
        self.fields['proveedor'].queryset = Proveedor.objects.filter(activo=True).order_by('razon_social')

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto is not None and monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor a cero.")
        return monto

    def clean_fecha(self):
        from django.utils import timezone
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha > timezone.now().date():
            raise forms.ValidationError("La fecha no puede ser futura.")
        return fecha


class PlanTratamientoForm(forms.ModelForm):
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre'),
        label="Paciente",
        empty_label="Seleccionar paciente",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    nombre = forms.CharField(
        max_length=150,
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    descripcion = forms.CharField(
        required=False,
        label="Descripción",
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'rows': 3})
    )
    fecha_inicio = forms.DateField(
        label="Fecha de Inicio",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    fecha_fin = forms.DateField(
        required=False,
        label="Fecha de Fin",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    observaciones = forms.CharField(
        required=False,
        label="Observaciones",
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'rows': 3})
    )

    class Meta:
        model = PlanTratamiento
        fields = ['paciente', 'nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'observaciones']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paciente'].queryset = Paciente.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre')

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            self.add_error('fecha_fin', "La fecha de fin no puede ser anterior a la fecha de inicio.")
        return cleaned_data


class ObjetivoTratamientoForm(forms.ModelForm):
    plan_tratamiento = forms.ModelChoiceField(
        queryset=PlanTratamiento.objects.filter(activo=True).select_related('paciente__persona').order_by('-fecha_inicio'),
        label="Plan de Tratamiento",
        empty_label="Seleccionar plan",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    descripcion = forms.CharField(
        label="Descripción",
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'rows': 3})
    )
    cumplido = forms.BooleanField(
        required=False,
        label="Cumplido",
        widget=forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-2 focus:ring-primary-500'})
    )

    class Meta:
        model = ObjetivoTratamiento
        fields = ['plan_tratamiento', 'descripcion', 'cumplido']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plan_tratamiento'].queryset = PlanTratamiento.objects.filter(activo=True).select_related('paciente__persona').order_by('-fecha_inicio')


class ActividadPlanForm(forms.ModelForm):
    plan_tratamiento = forms.ModelChoiceField(
        queryset=PlanTratamiento.objects.filter(activo=True).select_related('paciente__persona').order_by('-fecha_inicio'),
        label="Plan de Tratamiento",
        empty_label="Seleccionar plan",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    servicio = forms.ModelChoiceField(
        queryset=Servicio.objects.filter(activo=True).select_related('tipo_servicio').order_by('tipo_servicio__nombre', 'nombre'),
        required=False,
        label="Servicio",
        empty_label="Seleccionar servicio (opcional)",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    descripcion = forms.CharField(
        label="Descripción",
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'rows': 3})
    )
    frecuencia_semanal = forms.IntegerField(
        required=False,
        label="Frecuencia Semanal",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )

    class Meta:
        model = ActividadPlan
        fields = ['plan_tratamiento', 'servicio', 'descripcion', 'frecuencia_semanal']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plan_tratamiento'].queryset = PlanTratamiento.objects.filter(activo=True).select_related('paciente__persona').order_by('-fecha_inicio')
        self.fields['servicio'].queryset = Servicio.objects.filter(activo=True).select_related('tipo_servicio').order_by('tipo_servicio__nombre', 'nombre')

    def clean_frecuencia_semanal(self):
        frecuencia = self.cleaned_data.get('frecuencia_semanal')
        if frecuencia is not None and frecuencia < 1:
            raise forms.ValidationError("La frecuencia semanal debe ser mayor o igual a 1.")
        return frecuencia


class HistorialMedicoForm(forms.ModelForm):
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre'),
        label="Paciente",
        empty_label="Seleccionar paciente",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    profesional = forms.ModelChoiceField(
        queryset=Empleado.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre'),
        label="Profesional",
        empty_label="Seleccionar profesional",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    fecha = forms.DateTimeField(
        label="Fecha",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    descripcion = forms.CharField(
        label="Descripción",
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'rows': 4})
    )
    observaciones = forms.CharField(
        required=False,
        label="Observaciones",
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'rows': 3})
    )

    class Meta:
        model = HistorialMedico
        fields = ['paciente', 'profesional', 'fecha', 'descripcion', 'observaciones']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paciente'].queryset = Paciente.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre')
        self.fields['profesional'].queryset = Empleado.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre')


class EvolucionSemanalForm(forms.ModelForm):
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre'),
        label="Paciente",
        empty_label="Seleccionar paciente",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    plan_tratamiento = forms.ModelChoiceField(
        queryset=PlanTratamiento.objects.filter(activo=True).select_related('paciente__persona').order_by('-fecha_inicio'),
        required=False,
        label="Plan de Tratamiento",
        empty_label="Seleccionar plan (opcional)",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    profesional = forms.ModelChoiceField(
        queryset=Empleado.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre'),
        label="Profesional",
        empty_label="Seleccionar profesional",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    fecha = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    descripcion = forms.CharField(
        label="Descripción",
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'rows': 4})
    )

    class Meta:
        model = EvolucionSemanal
        fields = ['paciente', 'plan_tratamiento', 'profesional', 'fecha', 'descripcion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paciente'].queryset = Paciente.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre')
        self.fields['plan_tratamiento'].queryset = PlanTratamiento.objects.filter(activo=True).select_related('paciente__persona').order_by('-fecha_inicio')
        self.fields['profesional'].queryset = Empleado.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre')


class RegistroActividadForm(forms.ModelForm):
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre'),
        label="Paciente",
        empty_label="Seleccionar paciente",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    actividad = forms.ModelChoiceField(
        queryset=ActividadPlan.objects.filter(activo=True).select_related('plan_tratamiento__paciente__persona', 'servicio').order_by('-plan_tratamiento__fecha_inicio'),
        label="Actividad",
        empty_label="Seleccionar actividad",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    profesional = forms.ModelChoiceField(
        queryset=Empleado.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre'),
        label="Profesional",
        empty_label="Seleccionar profesional",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    fecha = forms.DateTimeField(
        label="Fecha",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    descripcion = forms.CharField(
        required=False,
        label="Descripción",
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'rows': 3})
    )
    realizado = forms.BooleanField(
        required=False,
        label="Realizado",
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-2 focus:ring-primary-500'})
    )

    class Meta:
        model = RegistroActividad
        fields = ['paciente', 'actividad', 'profesional', 'fecha', 'descripcion', 'realizado']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paciente'].queryset = Paciente.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre')
        self.fields['actividad'].queryset = ActividadPlan.objects.filter(activo=True).select_related('plan_tratamiento__paciente__persona', 'servicio').order_by('-plan_tratamiento__fecha_inicio')
        self.fields['profesional'].queryset = Empleado.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre')


class NotaImportanteForm(forms.ModelForm):
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre'),
        label="Paciente",
        empty_label="Seleccionar paciente",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    profesional = forms.ModelChoiceField(
        queryset=Empleado.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre'),
        label="Profesional",
        empty_label="Seleccionar profesional",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    titulo = forms.CharField(
        max_length=150,
        label="Título",
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    descripcion = forms.CharField(
        label="Descripción",
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'rows': 4})
    )

    class Meta:
        model = NotaImportante
        fields = ['paciente', 'profesional', 'titulo', 'descripcion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paciente'].queryset = Paciente.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre')
        self.fields['profesional'].queryset = Empleado.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre')


class TurnoForm(forms.ModelForm):
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre'),
        label="Concurrente",
        empty_label="Seleccionar concurrente",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    profesional = forms.ModelChoiceField(
        queryset=Empleado.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre'),
        label="Profesional",
        empty_label="Seleccionar profesional",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    servicio = forms.ModelChoiceField(
        queryset=Servicio.objects.filter(activo=True).select_related('tipo_servicio').order_by('tipo_servicio__nombre', 'nombre'),
        label="Servicio / Motivo",
        empty_label="Seleccionar servicio",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    fecha = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    hora_inicio = forms.TimeField(
        label="Hora de Inicio",
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    hora_fin = forms.TimeField(
        label="Hora de Fin",
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    estado = forms.ChoiceField(
        choices=EstadoTurno.choices,
        label="Estado",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'})
    )
    observaciones = forms.CharField(
        required=False,
        label="Observaciones",
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'rows': 3})
    )

    class Meta:
        model = Turno
        fields = ['paciente', 'profesional', 'servicio', 'fecha', 'hora_inicio', 'hora_fin', 'estado', 'observaciones']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['paciente'].queryset = Paciente.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre')
        self.fields['profesional'].queryset = Empleado.objects.filter(activo=True).select_related('persona').order_by('persona__apellido', 'persona__nombre')
        self.fields['servicio'].queryset = Servicio.objects.filter(activo=True).select_related('tipo_servicio').order_by('tipo_servicio__nombre', 'nombre')
        
        if user and not (user.is_superuser or user.rol in ['admin', 'recepcionista', 'orientador']):
            self.fields['profesional'].widget = forms.HiddenInput()
            if hasattr(user, 'empleado') and user.empleado:
                self.fields['profesional'].initial = user.empleado

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        fecha = cleaned_data.get('fecha')
        profesional = cleaned_data.get('profesional')
        
        if hora_inicio and hora_fin and hora_fin <= hora_inicio:
            self.add_error('hora_fin', "La hora de fin debe ser posterior a la hora de inicio.")
        
        if fecha and hora_inicio and not self.instance.pk:
            from django.utils import timezone
            from datetime import datetime
            turno_datetime = timezone.make_aware(datetime.combine(fecha, hora_inicio))
            if turno_datetime < timezone.now():
                self.add_error('fecha', "No se puede agendar un turno en el pasado.")
        
        if fecha and hora_inicio and hora_fin and profesional:
            from django.db.models import Q
            solapamiento = Turno.objects.filter(
                profesional=profesional,
                fecha=fecha,
                estado__in=[EstadoTurno.PENDIENTE, EstadoTurno.CONFIRMADO],
            ).filter(
                Q(hora_inicio__lt=hora_fin) & Q(hora_fin__gt=hora_inicio)
            )
            if self.instance.pk:
                solapamiento = solapamiento.exclude(pk=self.instance.pk)
            if solapamiento.exists():
                self.add_error('hora_inicio', "El profesional ya tiene un turno en ese horario.")
        
        return cleaned_data
