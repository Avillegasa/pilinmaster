from django import forms
from .models import Reporte

class ReporteForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = [
            'nombre', 'tipo', 'formato_preferido', 'fecha_desde', 'fecha_hasta',
            'es_favorito', 'puesto', 'edificio'
        ]
        widgets = {
            'fecha_desde': forms.DateInput(attrs={'type': 'date'}),
            'fecha_hasta': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        tipo_inicial = kwargs.get('initial', {}).get('tipo')
        super().__init__(*args, **kwargs)
        if tipo_inicial or self.instance.pk is None:
            self.fields['tipo'].widget = forms.HiddenInput()