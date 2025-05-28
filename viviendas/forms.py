from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from usuarios.models import Usuario
from .models import Edificio, Vivienda, Residente

class EdificioForm(forms.ModelForm):
    class Meta:
        model = Edificio
        fields = ['nombre', 'direccion', 'pisos', 'fecha_construccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del edificio'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'}),
            'pisos': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 50}),
            'fecha_construccion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        }
        labels = {
            'nombre': 'Nombre del Edificio',
            'direccion': 'Dirección',
            'pisos': 'Número de Pisos',
            'fecha_construccion': 'Fecha de Construcción'
        }

class EdificioBajaForm(forms.ModelForm):
    fecha_baja = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date(),
        help_text="Fecha en la que se da de baja el edificio."
    )
    
    motivo_baja = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=True,
        help_text="Motivo por el cual se da de baja el edificio."
    )
    
    confirmar_viviendas = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Confirmo que he revisado las viviendas asociadas a este edificio."
    )
    
    class Meta:
        model = Edificio
        fields = ['fecha_baja', 'motivo_baja']

# ✅ CORRECCIÓN CRÍTICA: Formulario de Vivienda mejorado
class ViviendaForm(forms.ModelForm):
    class Meta:
        model = Vivienda
        fields = ['edificio', 'numero', 'piso', 'metros_cuadrados', 'habitaciones', 'baños', 'estado']
        widgets = {
            'edificio': forms.Select(attrs={'class': 'form-select'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 101, A-5, etc.'}),
            'piso': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 50}),
            'metros_cuadrados': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '10'}),
            'habitaciones': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'baños': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'estado': forms.Select(attrs={'class': 'form-select'})
        }
        labels = {
            'edificio': 'Edificio',
            'numero': 'Número/Identificación',
            'piso': 'Piso',
            'metros_cuadrados': 'Metros Cuadrados',
            'habitaciones': 'Habitaciones',
            'baños': 'Baños',
            'estado': 'Estado Inicial'
        }
        help_texts = {
            'numero': 'Identificación única de la vivienda (ej: 101, A-5, etc.)',
            'metros_cuadrados': 'Área en metros cuadrados',
            'estado': 'Estado inicial de la vivienda'
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ CORRECCIÓN: Filtrar solo edificios activos
        self.fields['edificio'].queryset = Edificio.objects.filter(activo=True).order_by('nombre')
        
        # ✅ VALIDACIÓN: Verificar que hay edificios disponibles
        if not self.fields['edificio'].queryset.exists():
            self.fields['edificio'].empty_label = "No hay edificios activos disponibles"
            
    def clean(self):
        cleaned_data = super().clean()
        edificio = cleaned_data.get('edificio')
        numero = cleaned_data.get('numero')
        piso = cleaned_data.get('piso')
        
        # ✅ VALIDACIÓN: Verificar que el edificio esté activo
        if edificio and not edificio.activo:
            raise ValidationError({
                'edificio': 'No se puede crear una vivienda en un edificio dado de baja.'
            })
        
        # ✅ VALIDACIÓN: Verificar que el piso no exceda los pisos del edificio
        if edificio and piso and piso > edificio.pisos:
            raise ValidationError({
                'piso': f'El piso no puede ser mayor a {edificio.pisos} (pisos del edificio).'
            })
        
        # ✅ VALIDACIÓN: Verificar unicidad de número por edificio (excluyendo la instancia actual)
        if edificio and numero:
            queryset = Vivienda.objects.filter(edificio=edificio, numero=numero)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise ValidationError({
                    'numero': f'Ya existe una vivienda con el número "{numero}" en el edificio "{edificio.nombre}".'
                })
        
        return cleaned_data

class ViviendaBajaForm(forms.ModelForm):
    """
    Formulario para dar de baja una vivienda.
    Permite ingresar el motivo y la fecha de la baja.
    """
    fecha_baja = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date(),
        help_text="Fecha en la que se da de baja la vivienda."
    )
    
    motivo_baja = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=True,
        help_text="Motivo por el cual se da de baja la vivienda."
    )
    
    confirmar_residentes = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Confirmo que he revisado y entiendo que los residentes asociados a esta vivienda perderán su asignación."
    )
    
    class Meta:
        model = Vivienda
        fields = ['fecha_baja', 'motivo_baja']

# ✅ CORRECCIÓN: Formulario de Residente mejorado
class ResidenteForm(forms.ModelForm):
    edificio = forms.ModelChoiceField(
        queryset=Edificio.objects.filter(activo=True).order_by('nombre'),
        required=False,
        label="Edificio",
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Seleccione el edificio para filtrar las viviendas disponibles"
    )
    
    class Meta:
        model = Residente
        fields = ['usuario', 'edificio', 'vivienda', 'es_propietario', 'vehiculos', 'activo']
        widgets = {
            'usuario': forms.Select(attrs={'class': 'form-select'}),
            'vivienda': forms.Select(attrs={'class': 'form-select'}),
            'es_propietario': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'vehiculos': forms.NumberInput(attrs={'min': 0, 'max': 10, 'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'usuario': 'Usuario',
            'vivienda': 'Vivienda',
            'es_propietario': '¿Es propietario?',
            'vehiculos': 'Cantidad de Vehículos',
            'activo': 'Residente Activo'
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ✅ CORRECCIÓN: Solo mostrar usuarios que no sean residentes activos
        usuarios_disponibles = Usuario.objects.filter(is_active=True)
        if not (self.instance and self.instance.pk):
            # En creación, excluir usuarios que ya son residentes activos
            usuarios_con_residente = Residente.objects.filter(activo=True).values_list('usuario_id', flat=True)
            usuarios_disponibles = usuarios_disponibles.exclude(id__in=usuarios_con_residente)
        
        self.fields['usuario'].queryset = usuarios_disponibles.order_by('first_name', 'last_name')
        
        # Si es un formulario de edición (instancia existente)
        if self.instance and self.instance.pk:
            # Si el residente ya tiene vivienda, preseleccionar el edificio
            if self.instance.vivienda:
                self.fields['edificio'].initial = self.instance.vivienda.edificio
                # Filtrar viviendas solo del edificio seleccionado y activas
                self.fields['vivienda'].queryset = Vivienda.objects.filter(
                    edificio=self.instance.vivienda.edificio,
                    activo=True
                ).order_by('piso', 'numero')
            else:
                # Si no tiene vivienda, mostrar todas las activas
                self.fields['vivienda'].queryset = Vivienda.objects.filter(
                    activo=True
                ).order_by('edificio__nombre', 'piso', 'numero')
        else:
            # En caso de creación, mostrar todas las viviendas activas inicialmente
            self.fields['vivienda'].queryset = Vivienda.objects.filter(
                activo=True
            ).order_by('edificio__nombre', 'piso', 'numero')
            
        # Hacer que el campo edificio no sea parte del modelo, es solo para filtrado
        self.fields['edificio'].required = False
        
        # ✅ VERIFICAR: Si no hay viviendas disponibles
        if not self.fields['vivienda'].queryset.exists():
            self.fields['vivienda'].empty_label = "No hay viviendas activas disponibles"
    
    def clean(self):
        cleaned_data = super().clean()
        usuario = cleaned_data.get('usuario')
        vivienda = cleaned_data.get('vivienda')
        
        # ✅ VALIDACIÓN: Verificar que la vivienda esté activa
        if vivienda and not vivienda.activo:
            raise ValidationError({
                'vivienda': 'No se puede asignar un residente a una vivienda dada de baja.'
            })
        
        # ✅ VALIDACIÓN: Verificar que el usuario esté activo
        if usuario and not usuario.is_active:
            raise ValidationError({
                'usuario': 'No se puede asignar una vivienda a un usuario inactivo.'
            })
        
        # ✅ VALIDACIÓN: Verificar que el usuario no sea ya residente activo en otra vivienda
        if usuario and vivienda:
            residente_existente = Residente.objects.filter(
                usuario=usuario, 
                activo=True
            ).exclude(pk=self.instance.pk if self.instance else None).first()
            
            if residente_existente:
                raise ValidationError({
                    'usuario': f'El usuario ya es residente activo en la vivienda {residente_existente.vivienda}.'
                })
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Sincronizar el estado activo con el usuario
        if instance.usuario:
            instance.activo = instance.usuario.is_active
        if commit:
            instance.save()
        return instance

# Agregar esta clase al final del archivo viviendas/forms.py

class ViviendaAltaForm(forms.ModelForm):
        """
        Formulario para dar de alta una vivienda.
        Permite ingresar el motivo y la fecha del alta.
        """
        fecha_alta = forms.DateField(
            widget=forms.DateInput(attrs={'type': 'date'}),
            initial=timezone.now().date(),
            help_text="Fecha en la que se da de alta la vivienda.",
            label="Fecha de Alta"
        )
        
        motivo_alta = forms.CharField(
            widget=forms.Textarea(attrs={'rows': 3}),
            required=True,
            help_text="Motivo por el cual se da de alta la vivienda (ej: reparaciones completadas, problema resuelto, etc.)",
            label="Motivo de Alta"
        )
        
        class Meta:
            model = Vivienda
            fields = []  # No necesitamos campos del modelo, solo los custom fields
            
        def save(self, commit=True):
            """
            Método personalizado para dar de alta la vivienda
            """
            instance = self.instance
            if commit:
                # Reactivar la vivienda
                instance.activo = True
                instance.estado = 'DESOCUPADO'  # Estado por defecto al dar de alta
                
                # Limpiar datos de baja
                instance.fecha_baja = None
                instance.motivo_baja = None
                
                # Registrar información del alta (opcional: podrías agregar estos campos al modelo)
                # instance.fecha_alta = self.cleaned_data['fecha_alta']
                # instance.motivo_alta = self.cleaned_data['motivo_alta']
                
                instance.save()
            return instance