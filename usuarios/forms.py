# Forms.py de usuarios
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario, Rol
import re
from viviendas.models import Edificio, Vivienda
from usuarios.models import Gerente, Vigilante
from viviendas.models import Vivienda, Residente

class UsuarioCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=254)
    edificio = forms.ModelChoiceField(
        queryset=Edificio.objects.all(),
        required=False,
        label="Edificio"
    )
    vivienda = forms.ModelChoiceField(
        queryset=Vivienda.objects.none(),  # Se filtrará dinámicamente
        required=False,
        label="Vivienda (solo para Residente)"
    )

    class Meta:
        model = Usuario
        fields = [
            'username',
            'email', 'first_name', 'last_name', 'telefono',
            'numero_documento', 'rol', 'foto',
            'password1', 'password2', 'edificio', 'vivienda'
        ]

    def __init__(self, *args, **kwargs):
        self.user_actual = kwargs.pop('user_actual', None)  # Aceptar el parámetro extra
        super().__init__(*args, **kwargs)
        # Si el rol "Personal" está presente en los datos o instancia, hacer campos opcionales
        rol_data = self.data.get('rol') or (self.instance.rol.id if self.instance and self.instance.rol else None)
        try:
            if rol_data:
                rol_obj = Rol.objects.get(id=rol_data)
                if rol_obj.nombre == "Personal":
                    self.fields['username'].required = False
                    self.fields['email'].required = False
                    self.fields['password1'].required = False
                    self.fields['password2'].required = False
        except Rol.DoesNotExist:
            pass


        # Filtrar viviendas si ya hay un edificio seleccionado
        if 'edificio' in self.data:
            try:
                edificio_id = int(self.data.get('edificio'))
                self.fields['vivienda'].queryset = Vivienda.objects.filter(
                    edificio_id=edificio_id,
                    estado='DESOCUPADO',
                    activo=True
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and hasattr(self.instance, 'residente'):
            self.fields['vivienda'].queryset = Vivienda.objects.filter(
                edificio=self.instance.residente.vivienda.edificio
            )

        # Filtrar roles si el usuario actual es Gerente (no puede ver "Administrador")
        if self.user_actual and hasattr(self.user_actual, 'rol'):
            if self.user_actual.rol.nombre == 'Gerente':
                self.fields['rol'].queryset = Rol.objects.exclude(nombre='Administrador')

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        edificio = cleaned_data.get('edificio')
        vivienda = cleaned_data.get('vivienda')
        if rol and rol.nombre == 'Personal':
            # No validar campos que serán ignorados
            return cleaned_data

        if rol and rol.nombre == 'Residente':
            if not edificio:
                self.add_error('edificio', 'Debes seleccionar un edificio para asignar al Residente.')
            if not vivienda:
                self.add_error('vivienda', 'Debes seleccionar una vivienda para asignar al Residente.')
            elif vivienda.edificio != edificio:
                self.add_error('vivienda', 'La vivienda no pertenece al edificio seleccionado.')

        if rol and rol.nombre in ['Gerente', 'Vigilante'] and not edificio:
            self.add_error('edificio', f'Debes seleccionar un edificio para asignar al rol {rol.nombre}.')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        rol = self.cleaned_data.get('rol')
        if rol and rol.nombre == 'Personal':
            return email  # Saltar validación
        if not email.endswith('@gmail.com'):
            raise forms.ValidationError("Solo se permiten correos de Gmail (@gmail.com).")
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está en uso.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip().lower()
        rol = self.cleaned_data.get('rol')
        if rol and rol.nombre == 'Personal':
            return username  # Saltar validación
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

    edificio = forms.ModelChoiceField(
        queryset=Edificio.objects.all(),
        required=False,
        label="Edificio (solo para Gerente)"
    )
    vivienda = forms.ModelChoiceField(
        queryset=Vivienda.objects.all(),
        required=False,
        label="Vivienda (solo para Residente)"
    )
    class Meta:
        model = Usuario
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'telefono', 'numero_documento', 'rol', 'foto'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            if hasattr(self.instance, 'gerente'):
                self.fields['edificio'].initial = self.instance.gerente.edificio
            elif hasattr(self.instance, 'vigilante'):
                self.fields['edificio'].initial = self.instance.vigilante.edificio
            if hasattr(self.instance, 'residente'):
                self.fields['edificio'].initial = self.instance.residente.vivienda.edificio
                self.fields['vivienda'].initial = self.instance.residente.vivienda


    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        edificio = cleaned_data.get('edificio')
        vivienda = cleaned_data.get('vivienda')

        if rol:
            if rol.nombre in ['Gerente', 'Vigilante'] and not edificio:
                self.add_error('edificio', f'Debes seleccionar un edificio para el rol {rol.nombre}.')
            if rol.nombre == 'Residente':
                if not vivienda:
                    self.add_error('vivienda', 'Debes seleccionar una vivienda para el Residente.')
                elif vivienda and edificio and vivienda.edificio != edificio:
                    self.add_error('vivienda', 'La vivienda no pertenece al edificio seleccionado.')

        return cleaned_data


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
        if Usuario.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está en uso por otro usuario.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        nueva_password = self.cleaned_data.get('nueva_password')
        edificio = self.cleaned_data.get('edificio')
        vivienda = self.cleaned_data.get('vivienda')

        if nueva_password:
            user.set_password(nueva_password)

        if commit:
            user.save()

            if user.rol:
                if user.rol.nombre == 'Gerente':
                    Gerente.objects.update_or_create(usuario=user, defaults={'edificio': edificio})
                    user.vigilante.delete() if hasattr(user, 'vigilante') else None
                    user.residente.delete() if hasattr(user, 'residente') else None

                elif user.rol.nombre == 'Vigilante':
                    Vigilante.objects.update_or_create(usuario=user, defaults={'edificio': edificio})
                    user.gerente.delete() if hasattr(user, 'gerente') else None
                    user.residente.delete() if hasattr(user, 'residente') else None

                elif user.rol.nombre == 'Residente':
                    Residente.objects.update_or_create(
                        usuario=user, 
                        defaults={'vivienda': vivienda}
                        )

                    # Eliminar otros roles si existen
                    if hasattr(user, 'gerente'):
                        user.gerente.delete()
                    if hasattr(user, 'vigilante'):
                        user.vigilante.delete()

        return user


class RolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(RolForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['nombre'].disabled = True  # Esto evita que se pueda editar el nombre
