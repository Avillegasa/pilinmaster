from django import forms
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

class MovimientoResidenteEntradaForm(forms.ModelForm):
    class Meta:
        model = MovimientoResidente
        fields = ('residente', 'vehiculo', 'placa_vehiculo')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar que solo se muestren residentes activos en el formulario
        self.fields['residente'].queryset = Residente.objects.filter(activo=True)
        self.fields['residente'].help_text = "Solo se muestran residentes activos"
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        import datetime
        instance.fecha_hora_entrada = datetime.datetime.now()
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
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        import datetime
        instance.fecha_hora_salida = datetime.datetime.now()
        if commit:
            instance.save()
        return instance