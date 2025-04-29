from django import forms
from .models import Edificio, Vivienda, Residente, TipoResidente

class EdificioForm(forms.ModelForm):
    class Meta:
        model = Edificio
        fields = '__all__'

class ViviendaForm(forms.ModelForm):
    class Meta:
        model = Vivienda
        fields = '__all__'

class TipoResidenteForm(forms.ModelForm):
    class Meta:
        model = TipoResidente
        fields = '__all__'

class ResidenteForm(forms.ModelForm):
    class Meta:
        model = Residente
        fields = ['usuario', 'vivienda', 'tipo_residente', 'vehiculos', 'activo']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir clases o atributos adicionales a los campos si es necesario
        self.fields['tipo_residente'].queryset = TipoResidente.objects.all().order_by('nombre')
        self.fields['tipo_residente'].empty_label = None  # Requiere que se seleccione un tipo