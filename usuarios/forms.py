from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario, Rol

class UsuarioCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'rol', 'telefono', 'tipo_documento', 'numero_documento', 'foto')

class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'rol', 'telefono', 'tipo_documento', 'numero_documento', 'foto')

class RolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = '__all__'