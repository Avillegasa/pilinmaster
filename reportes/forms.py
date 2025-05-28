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


class ExportForm(forms.Form):
    FORMATO_CHOICES = [
        ('PDF', 'PDF'),
        ('EXCEL', 'Excel'),
        ('CSV', 'CSV'),
        ('HTML', 'HTML'),
    ]
    
    formato = forms.ChoiceField(
        choices=FORMATO_CHOICES,
        initial='PDF',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    incluir_graficos = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    paginar = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
