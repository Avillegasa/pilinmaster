from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario, Rol
import re

class UsuarioCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=254)

    class Meta:
        model = Usuario
        fields = [
            'username',
            'email', 'first_name', 'last_name', 'telefono',
            'numero_documento', 'rol', 'foto',
            'password1', 'password2'
        ]

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.endswith('@gmail.com'):
            raise forms.ValidationError("Solo se permiten correos de Gmail (@gmail.com).")
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está en uso.")
        return email


    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip().lower()
        if not username:
            raise forms.ValidationError("Este campo es obligatorio.")
        if ' ' in username:
            raise forms.ValidationError("El nombre de usuario no debe contener espacios.")
        if len(username) > 150:
            raise forms.ValidationError("El nombre de usuario no debe tener más de 150 caracteres.")
        return username

    def clean_first_name(self):
        nombre = self.cleaned_data.get('first_name', '').strip()
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$', nombre):
            raise forms.ValidationError("El nombre solo debe contener letras y espacios.")
        return nombre.title()

    def clean_last_name(self):
        apellido = self.cleaned_data.get('last_name', '').strip()
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$', apellido):
            raise forms.ValidationError("El apellido solo debe contener letras y espacios.")
        return apellido.title()


    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        if not telefono.isdigit():
            raise forms.ValidationError("El teléfono solo debe contener números.")
        return telefono
    
    def clean_numero_documento(self):
        numero_documento = self.cleaned_data.get('numero_documento', '').strip()
        if not numero_documento.isdigit():
            raise forms.ValidationError("La Cédula solo debe contener números.")
        return numero_documento

class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'rol', 'telefono', 'numero_documento', 'foto')

class UsuarioEditForm(forms.ModelForm):
    nueva_password = forms.CharField(
        label="Nueva contraseña",
        required=False,
        widget=forms.PasswordInput,
        help_text="Déjalo vacío si no deseas cambiar la contraseña."
    )

    class Meta:
        model = Usuario
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'telefono', 'numero_documento', 'rol', 'foto'
        )
    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip().lower()
        if not username:
            raise forms.ValidationError("Este campo es obligatorio.")
        if ' ' in username:
            raise forms.ValidationError("El nombre de usuario no debe contener espacios.")
        if len(username) > 150:
            raise forms.ValidationError("El nombre de usuario no debe tener más de 150 caracteres.")
        return username
    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.endswith('@gmail.com'):
            raise forms.ValidationError("Solo se permiten correos de Gmail (@gmail.com).")
        # Validación extra si no quieres duplicados entre otros usuarios
        if Usuario.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está en uso por otro usuario.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        nueva_password = self.cleaned_data.get('nueva_password')
        if nueva_password:
            user.set_password(nueva_password)
        if commit:
            user.save()
        return user

class RolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = '__all__'
