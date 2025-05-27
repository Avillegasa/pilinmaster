from django import forms
from django.utils import timezone
from .models import Visita, MovimientoResidente
from viviendas.models import Residente, Vivienda

class VisitaForm(forms.ModelForm):
    class Meta:
        model = Visita
        fields = ('nombre_visitante', 'documento_visitante', 'vivienda_destino', 'residente_autoriza', 'motivo')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar que solo se muestren residentes activos en el formulario
        self.fields['residente_autoriza'].queryset = Residente.objects.filter(activo=True)
        
        # Actualizar etiquetas y mensajes de ayuda
        self.fields['vivienda_destino'].help_text = "Seleccione la vivienda que será visitada"
        self.fields['residente_autoriza'].help_text = "Residente que autoriza la visita (solo se muestran residentes activos)"
        
        # Añadir validaciones adicionales
        self.fields['nombre_visitante'].widget.attrs.update({'class': 'form-control'})
        self.fields['documento_visitante'].widget.attrs.update({'class': 'form-control'})
        self.fields['motivo'].widget.attrs.update({'class': 'form-control', 'rows': 3})
    
    def clean_documento_visitante(self):
        documento = self.cleaned_data.get('documento_visitante')
        if documento and len(documento) < 6:
            raise forms.ValidationError("El documento debe tener al menos 6 caracteres")
        return documento
    
    def clean_nombre_visitante(self):
        nombre = self.cleaned_data.get('nombre_visitante')
        if nombre and len(nombre.split()) < 2:
            raise forms.ValidationError("Ingrese nombre y apellido completos")
        return nombre

class MovimientoResidenteEntradaForm(forms.ModelForm):
    class Meta:
        model = MovimientoResidente
        fields = ('residente', 'vehiculo', 'placa_vehiculo')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar que solo se muestren residentes activos en el formulario
        self.fields['residente'].queryset = Residente.objects.filter(activo=True)
        self.fields['residente'].help_text = "Solo se muestran residentes activos"
        
        # Añadir atributos para mejor UX
        self.fields['vehiculo'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['placa_vehiculo'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ej: ABC-123'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        vehiculo = cleaned_data.get('vehiculo')
        placa_vehiculo = cleaned_data.get('placa_vehiculo')
        residente = cleaned_data.get('residente')
        
        # Validar que si tiene vehículo, debe ingresar placa
        if vehiculo and not placa_vehiculo:
            raise forms.ValidationError("Si ingresa con vehículo, debe especificar la placa")
        
        # Validar que el residente no tenga ya una entrada activa
        if residente:
            entrada_activa = MovimientoResidente.objects.filter(
                residente=residente,
                fecha_hora_entrada__isnull=False,
                fecha_hora_salida__isnull=True
            ).exists()
            
            if entrada_activa:
                raise forms.ValidationError(f"El residente {residente} ya tiene una entrada registrada sin salida correspondiente")
        
        return cleaned_data
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.fecha_hora_entrada = timezone.now()
        instance.fecha_hora_salida = None  # Asegurar que la salida esté vacía
        if commit:
            instance.save()
        return instance

class MovimientoResidenteSalidaForm(forms.ModelForm):
    class Meta:
        model = MovimientoResidente
        fields = ('residente', 'vehiculo', 'placa_vehiculo')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar que solo se muestren residentes activos en el formulario
        self.fields['residente'].queryset = Residente.objects.filter(activo=True)
        self.fields['residente'].help_text = "Solo se muestran residentes activos"
        
        # Añadir atributos para mejor UX
        self.fields['vehiculo'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['placa_vehiculo'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ej: ABC-123'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        vehiculo = cleaned_data.get('vehiculo')
        placa_vehiculo = cleaned_data.get('placa_vehiculo')
        residente = cleaned_data.get('residente')
        
        # Validar que si tiene vehículo, debe ingresar placa
        if vehiculo and not placa_vehiculo:
            raise forms.ValidationError("Si sale con vehículo, debe especificar la placa")
        
        # Validar que el residente no tenga ya una salida activa
        if residente:
            salida_activa = MovimientoResidente.objects.filter(
                residente=residente,
                fecha_hora_salida__isnull=False,
                fecha_hora_entrada__isnull=True
            ).exists()
            
            if salida_activa:
                raise forms.ValidationError(f"El residente {residente} ya tiene una salida registrada sin entrada correspondiente")
        
        return cleaned_data
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.fecha_hora_salida = timezone.now()
        instance.fecha_hora_entrada = None  # Asegurar que la entrada esté vacía
        if commit:
            instance.save()
        return instance