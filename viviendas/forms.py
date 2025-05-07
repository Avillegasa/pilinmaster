from django import forms
from django.utils import timezone
from .models import Edificio, Vivienda, Residente, TipoResidente

class EdificioForm(forms.ModelForm):
    class Meta:
        model = Edificio
        fields = '__all__'
        widgets = {
            'fecha_construccion': forms.DateInput(attrs={'type': 'date'})
        }

class ViviendaForm(forms.ModelForm):
    class Meta:
        model = Vivienda
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['edificio'].queryset = Edificio.objects.all().order_by('nombre')


class ViviendaBajaForm(forms.ModelForm):
    """
    Formulario para dar de baja una vivienda.
    Permite ingresar el motivo y la fecha de la baja.
    """
    fecha_baja = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date(),
        help_text="Fecha en la que se da de baja la vivienda."
    )
    
    motivo_baja = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        help_text="Motivo por el cual se da de baja la vivienda."
    )
    
    confirmar_residentes = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(),
        help_text="Confirmo que he revisado y entiendo que los residentes asociados a esta vivienda perderán su asignación."
    )
    
    class Meta:
        model = Vivienda
        fields = ['fecha_baja', 'motivo_baja']

class TipoResidenteForm(forms.ModelForm):
    class Meta:
        model = TipoResidente
        fields = '__all__'

class ResidenteForm(forms.ModelForm):
    edificio = forms.ModelChoiceField(
        queryset=Edificio.objects.all().order_by('nombre'),
        required=False,
        label="Edificio",
        help_text="Seleccione el edificio para filtrar las viviendas disponibles"
    )
    
    class Meta:
        model = Residente
        fields = ['usuario', 'edificio', 'vivienda', 'tipo_residente', 'vehiculos', 'activo']
        widgets = {
            'tipo_residente': forms.Select(attrs={'class': 'form-select'}),
            'vivienda': forms.Select(attrs={'class': 'form-select'}),
            'usuario': forms.Select(attrs={'class': 'form-select'}),
            'vehiculos': forms.NumberInput(attrs={'min': 0, 'max': 10}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir clases o atributos adicionales a los campos si es necesario
        self.fields['tipo_residente'].queryset = TipoResidente.objects.all().order_by('nombre')
        self.fields['tipo_residente'].empty_label = None  # Requiere que se seleccione un tipo
        
        # Si es un formulario de edición (instancia existente)
        if self.instance and self.instance.pk:
            # Si el residente ya tiene vivienda, preseleccionar el edificio
            if self.instance.vivienda:
                self.fields['edificio'].initial = self.instance.vivienda.edificio
                # Filtrar viviendas solo del edificio seleccionado
                self.fields['vivienda'].queryset = Vivienda.objects.filter(
                    edificio=self.instance.vivienda.edificio
                ).order_by('piso', 'numero')
            else:
                # Si no tiene vivienda, mostrar todas
                self.fields['vivienda'].queryset = Vivienda.objects.all().order_by('edificio__nombre', 'piso', 'numero')
        else:
            # En caso de creación, mostrar todas las viviendas inicialmente
            self.fields['vivienda'].queryset = Vivienda.objects.all().order_by('edificio__nombre', 'piso', 'numero')
            
        # Hacer que el campo edificio no sea parte del modelo, es solo para filtrado
        self.fields['edificio'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        # Aquí podríamos añadir validaciones adicionales
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Asegurarse de que el campo es_propietario se alinee con el tipo de residente
        if instance.tipo_residente:
            instance.es_propietario = instance.tipo_residente.es_propietario
        
        if commit:
            instance.save()
        return instance