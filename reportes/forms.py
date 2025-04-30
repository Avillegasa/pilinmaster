from django import forms
from django.utils import timezone
from .models import ReporteConfig
from viviendas.models import Edificio
from usuarios.models import Rol

class ReporteConfigForm(forms.ModelForm):
    """Formulario base para configurar reportes"""
    class Meta:
        model = ReporteConfig
        fields = ('nombre', 'tipo', 'fecha_desde', 'fecha_hasta', 'formato_preferido', 'es_favorito')
        widgets = {
            'fecha_desde': forms.DateInput(attrs={'type': 'date'}),
            'fecha_hasta': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializar la fecha hasta como hoy y desde como 30 días atrás por defecto
        if not self.instance.pk:
            self.fields['fecha_hasta'].initial = timezone.now().date()
            self.fields['fecha_desde'].initial = timezone.now().date() - timezone.timedelta(days=30)


class ReporteAccesosForm(ReporteConfigForm):
    """Formulario específico para reportes de accesos"""
    edificio = forms.ModelChoiceField(
        queryset=Edificio.objects.all(),
        required=False,
        label="Filtrar por Edificio",
    )
    
    tipo_visita = forms.ChoiceField(
        choices=[('', 'Todos'), ('ACTIVA', 'Visitas Activas'), ('FINALIZADA', 'Visitas Finalizadas')],
        required=False,
        label="Estado de la Visita"
    )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Guardar los filtros específicos en el campo JSON
        instance.filtros = {
            'edificio': self.cleaned_data.get('edificio').id if self.cleaned_data.get('edificio') else None,
            'tipo_visita': self.cleaned_data.get('tipo_visita')
        }
        if commit:
            instance.save()
        return instance


class ReporteResidentesForm(ReporteConfigForm):
    """Formulario específico para reportes de residentes"""
    edificio = forms.ModelChoiceField(
        queryset=Edificio.objects.all(),
        required=False,
        label="Filtrar por Edificio",
    )
    
    tipo_residente = forms.MultipleChoiceField(
        choices=[],  # Se llena dinámicamente en __init__
        required=False,
        label="Tipo de Residente",
        widget=forms.CheckboxSelectMultiple()
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos'), ('activo', 'Activos'), ('inactivo', 'Inactivos')],
        required=False,
        label="Estado"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cargar dinámicamente los tipos de residentes desde el modelo
        from viviendas.models import TipoResidente
        self.fields['tipo_residente'].choices = [
            (tipo.id, tipo.nombre) for tipo in TipoResidente.objects.all()
        ]
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Guardar los filtros específicos en el campo JSON
        instance.filtros = {
            'edificio': self.cleaned_data.get('edificio').id if self.cleaned_data.get('edificio') else None,
            'tipo_residente': list(self.cleaned_data.get('tipo_residente', [])),
            'estado': self.cleaned_data.get('estado')
        }
        if commit:
            instance.save()
        return instance


class ReporteViviendasForm(ReporteConfigForm):
    """Formulario específico para reportes de viviendas"""
    edificio = forms.ModelChoiceField(
        queryset=Edificio.objects.all(),
        required=False,
        label="Filtrar por Edificio",
    )
    
    estado = forms.MultipleChoiceField(
        choices=[
            ('OCUPADO', 'Ocupadas'),
            ('DESOCUPADO', 'Desocupadas'),
            ('MANTENIMIENTO', 'En Mantenimiento')
        ],
        required=False,
        label="Estado de la Vivienda",
        widget=forms.CheckboxSelectMultiple()
    )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Guardar los filtros específicos en el campo JSON
        instance.filtros = {
            'edificio': self.cleaned_data.get('edificio').id if self.cleaned_data.get('edificio') else None,
            'estado': list(self.cleaned_data.get('estado', []))
        }
        if commit:
            instance.save()
        return instance


class ReportePersonalForm(ReporteConfigForm):
    """Formulario específico para reportes de personal"""
    puesto = forms.MultipleChoiceField(
        choices=[],  # Se llena dinámicamente en __init__
        required=False,
        label="Puesto de Trabajo",
        widget=forms.CheckboxSelectMultiple()
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos'), ('activo', 'Activos'), ('inactivo', 'Inactivos')],
        required=False,
        label="Estado"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cargar dinámicamente los puestos desde el modelo
        from personal.models import Puesto
        self.fields['puesto'].choices = [
            (puesto.id, puesto.nombre) for puesto in Puesto.objects.all()
        ]
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Guardar los filtros específicos en el campo JSON
        instance.filtros = {
            'puesto': list(self.cleaned_data.get('puesto', [])),
            'estado': self.cleaned_data.get('estado')
        }
        if commit:
            instance.save()
        return instance


class ExportReportForm(forms.Form):
    """Formulario para exportar reportes en diferentes formatos"""
    formato = forms.ChoiceField(
        choices=ReporteConfig.FORMATOS,
        required=True,
        label="Formato de Exportación",
        initial='PDF'
    )
    
    incluir_graficos = forms.BooleanField(
        required=False,
        initial=True,
        label="Incluir Gráficos",
        help_text="Incluir gráficos en el reporte (solo en PDF y HTML)"
    )
    
    paginar = forms.BooleanField(
        required=False,
        initial=True,
        label="Paginar Resultados",
        help_text="Dividir el reporte en páginas (solo en PDF)"
    )
    
    orientacion = forms.ChoiceField(
        choices=[('portrait', 'Vertical'), ('landscape', 'Apaisado')],
        required=True,
        label="Orientación",
        initial='portrait',
        help_text="Orientación del documento (solo en PDF)"
    )