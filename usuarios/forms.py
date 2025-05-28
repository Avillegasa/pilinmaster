from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import Usuario, Rol

class UsuarioCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, label='Nombres')
    last_name = forms.CharField(max_length=150, required=True, label='Apellidos')
    email = forms.EmailField(required=True, label='Email')
    rol = forms.ModelChoiceField(queryset=Rol.objects.all(), required=False, label='Rol')
    telefono = forms.CharField(
        max_length=15, 
        required=False, 
        label='Teléfono',
        help_text='Solo números. Ej: 70123456',
        widget=forms.TextInput(attrs={
            'pattern': '[0-9]*',
            'inputmode': 'numeric',
            'placeholder': '70123456'
        })
    )
    tipo_documento = forms.ChoiceField(
        choices=[('CEDULA', 'Cédula de Identidad')], 
        initial='CEDULA',
        label='Tipo de Documento'
    )
    numero_documento = forms.CharField(
        max_length=20, 
        required=False, 
        label='Número de Documento',
        help_text='Solo números. Mínimo 7 caracteres.',
        widget=forms.TextInput(attrs={
            'pattern': '[0-9]*',
            'inputmode': 'numeric',
            'placeholder': '1234567'
        })
    )

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 
                 'rol', 'telefono', 'tipo_documento', 'numero_documento')

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        if telefono:
            # ✅ VALIDAR QUE SOLO CONTENGA NÚMEROS
            if not telefono.isdigit():
                raise ValidationError('El teléfono debe contener solo números.')
            
            # ✅ VALIDAR LONGITUD MÍNIMA Y MÁXIMA
            if len(telefono) < 7:
                raise ValidationError('El teléfono debe tener al menos 7 dígitos.')
            if len(telefono) > 15:
                raise ValidationError('El teléfono no puede tener más de 15 dígitos.')
                
        return telefono

    def clean_numero_documento(self):
        numero = self.cleaned_data.get('numero_documento', '').strip()
        if numero:
            # ✅ VALIDAR QUE SOLO CONTENGA NÚMEROS
            if not numero.isdigit():
                raise ValidationError('El número de documento debe contener solo números.')
            
            # ✅ VALIDAR LONGITUD MÍNIMA
            if len(numero) < 7:
                raise ValidationError('El número de documento debe tener al menos 7 dígitos.')
                
        return numero

class UsuarioChangeForm(UserChangeForm):
    first_name = forms.CharField(max_length=150, required=True, label='Nombres')
    last_name = forms.CharField(max_length=150, required=True, label='Apellidos')
    email = forms.EmailField(required=True, label='Email')
    rol = forms.ModelChoiceField(queryset=Rol.objects.all(), required=False, label='Rol')
    telefono = forms.CharField(
        max_length=15, 
        required=False, 
        label='Teléfono',
        help_text='Solo números. Ej: 70123456',
        widget=forms.TextInput(attrs={
            'pattern': '[0-9]*',
            'inputmode': 'numeric',
            'placeholder': '70123456'
        })
    )
    tipo_documento = forms.ChoiceField(
        choices=[('CEDULA', 'Cédula de Identidad')], 
        initial='CEDULA',
        label='Tipo de Documento'
    )
    numero_documento = forms.CharField(
        max_length=20, 
        required=False, 
        label='Número de Documento',
        help_text='Solo números. Mínimo 7 caracteres.',
        widget=forms.TextInput(attrs={
            'pattern': '[0-9]*',
            'inputmode': 'numeric',
            'placeholder': '1234567'
        })
    )

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 
                 'rol', 'telefono', 'tipo_documento', 'numero_documento', 'is_active')

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        if telefono:
            # ✅ VALIDAR QUE SOLO CONTENGA NÚMEROS
            if not telefono.isdigit():
                raise ValidationError('El teléfono debe contener solo números.')
            
            # ✅ VALIDAR LONGITUD MÍNIMA Y MÁXIMA
            if len(telefono) < 7:
                raise ValidationError('El teléfono debe tener al menos 7 dígitos.')
            if len(telefono) > 15:
                raise ValidationError('El teléfono no puede tener más de 15 dígitos.')
                
        return telefono

    def clean_numero_documento(self):
        numero = self.cleaned_data.get('numero_documento', '').strip()
        if numero:
            # ✅ VALIDAR QUE SOLO CONTENGA NÚMEROS
            if not numero.isdigit():
                raise ValidationError('El número de documento debe contener solo números.')
            
            # ✅ VALIDAR LONGITUD MÍNIMA
            if len(numero) < 7:
                raise ValidationError('El número de documento debe tener al menos 7 dígitos.')
                
        return numero

class RolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }