from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario, Rol

class UsuarioCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=254)

    class Meta:
        model = Usuario
        fields = [
            'username',  # AÑADIDO
            'email', 'first_name', 'last_name', 'telefono',
            'tipo_documento', 'numero_documento', 'rol', 'foto',
            'password1', 'password2'
        ]
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está en uso.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip().lower()
        if not username:
            raise forms.ValidationError("Este campo es obligatorio.")
        if ' ' in username:
            raise forms.ValidationError("El nombre de usuario no debe contener espacios.")
        if len(username) > 30:
            raise forms.ValidationError("El nombre de usuario no debe tener más de 30 caracteres.")
        return username

    def clean_last_name(self):
        apellido = self.cleaned_data['last_name']
        if len(apellido) > 30:
            raise forms.ValidationError("El apellido no debe tener más de 30 caracteres.")
        return apellido

class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'rol', 'telefono', 'tipo_documento', 'numero_documento', 'foto')

class RolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = '__all__'
