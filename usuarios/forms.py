from django import forms
from django.contrib.auth import get_user_model
from pacientes.models import AreaInterdisciplinaria
from usuarios.models import RolUsuario

Usuario = get_user_model()

# Roles que requieren área (profesionales de salud)
ROLES_PROFESIONALES = {
    RolUsuario.PSICOLOGO,
    RolUsuario.MEDICO,
    RolUsuario.TRABAJADOR_SOCIAL,
    RolUsuario.KINESIOLOGO,
    RolUsuario.PSICOMOTRICISTA,
    RolUsuario.NUTRICIONISTA,
    RolUsuario.PSICOPEDAGOGO,
    RolUsuario.PEDAGOGO,
    RolUsuario.ENFERMERO,
    RolUsuario.ORIENTADOR,
}


class UsuarioAdminForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'autocomplete': 'new-password'}),
        help_text="Mínimo 8 caracteres.",
        required=True,
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors', 'autocomplete': 'new-password'}),
        strip=False,
        help_text="Ingrese la misma contraseña que antes, para verificación.",
        required=True,
    )
    cambiar_password = forms.BooleanField(
        required=False,
        label="¿Desea cambiar la contraseña?",
        widget=forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500'}),
    )

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'rol', 'area']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'}),
            'rol': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'}),
            'area': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['area'].queryset = AreaInterdisciplinaria.objects.filter(activo=True)
        self.fields['area'].required = False
        self.fields['area'].empty_label = "— Sin área —"
        self.fields['rol'].choices = RolUsuario.choices
        
        is_editing = self.instance and self.instance.pk
        if is_editing:
            # En edición, ocultar password1/password2 y mostrar checkbox
            self.fields.pop('password1', None)
            self.fields.pop('password2', None)
        else:
            # En creación, ocultar checkbox
            self.fields.pop('cambiar_password', None)

    def clean_username(self):
        username = self.cleaned_data['username']
        qs = Usuario.objects.filter(username__iexact=username)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            qs = Usuario.objects.filter(email__iexact=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Este email ya está registrado.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        area = cleaned_data.get('area')
        is_editing = self.instance and self.instance.pk

        # Validar que los roles profesionales tengan área asignada
        if rol in ROLES_PROFESIONALES and not area:
            self.add_error('area', "Este rol profesional requiere un área asignada.")

        # Validar que roles administrativos no tengan área (opcional)
        if rol in {RolUsuario.ADMIN, RolUsuario.RECEPCIONISTA} and area:
            pass

        # En edición, validar contraseña solo si se marcó el checkbox
        if is_editing:
            cambiar_password = cleaned_data.get('cambiar_password')
            if cambiar_password:
                # Re-validar password1 y password2 desde POST data ya que no están en fields
                password1 = self.data.get('password1')
                password2 = self.data.get('password2')
                if not password1 or not password2:
                    self.add_error('cambiar_password', "Debe ingresar la nueva contraseña y su confirmación.")
                elif password1 != password2:
                    self.add_error('cambiar_password', "Las contraseñas no coinciden.")
                elif len(password1) < 8:
                    self.add_error('cambiar_password', "La contraseña debe tener al menos 8 caracteres.")
                else:
                    # Guardar la password validada en cleaned_data para save()
                    cleaned_data['password1'] = password1
            else:
                cleaned_data['password1'] = None

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user