from django import forms
from .models import Visita, MovimientoResidente

class VisitaForm(forms.ModelForm):
    class Meta:
        model = Visita
        fields = ('nombre_visitante', 'documento_visitante', 'vivienda_destino', 'residente_autoriza', 'motivo')

class MovimientoResidenteEntradaForm(forms.ModelForm):
    class Meta:
        model = MovimientoResidente
        fields = ('residente', 'vehiculo', 'placa_vehiculo')
        
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
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        import datetime
        instance.fecha_hora_salida = datetime.datetime.now()
        if commit:
            instance.save()
        return instance