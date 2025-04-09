from django import forms
from .models import Edificio, Vivienda, Residente

class EdificioForm(forms.ModelForm):
    class Meta:
        model = Edificio
        fields = '__all__'

class ViviendaForm(forms.ModelForm):
    class Meta:
        model = Vivienda
        fields = '__all__'

class ResidenteForm(forms.ModelForm):
    class Meta:
        model = Residente
        fields = '__all__'