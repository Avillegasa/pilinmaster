from django import forms
from .models import Puesto, Empleado, Asignacion, ComentarioAsignacion
from usuarios.models import Usuario, Rol
from viviendas.models import Edificio, Vivienda

class PuestoForm(forms.ModelForm):
    class Meta:
        model = Puesto
        fields = '__all__'

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = [
            'usuario', 'puesto', 'fecha_contratacion', 'tipo_contrato', 
            'salario', 'contacto_emergencia', 'telefono_emergencia', 
            'especialidad', 'activo'
        ]
        widgets = {
            'fecha_contratacion': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar usuarios que no estén ya asignados a un empleado existente
        # excepto el usuario actual en caso de edición
        usuarios_existentes = Empleado.objects.all()
        if self.instance and self.instance.pk:
            usuarios_existentes = usuarios_existentes.exclude(pk=self.instance.pk)
        
        usuarios_ids = usuarios_existentes.values_list('usuario_id', flat=True)
        self.fields['usuario'].queryset = Usuario.objects.exclude(
            id__in=usuarios_ids
        ).order_by('first_name', 'last_name')

class AsignacionForm(forms.ModelForm):
    edificio = forms.ModelChoiceField(
        queryset=Edificio.objects.all().order_by('nombre'),
        required=False,
        label="Edificio",
        help_text="Seleccione el edificio para filtrar las viviendas disponibles"
    )
    
    class Meta:
        model = Asignacion
        fields = [
            'empleado', 'tipo', 'titulo', 'descripcion', 'fecha_inicio',
            'fecha_fin', 'edificio', 'vivienda', 'estado', 'prioridad', 'notas'
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        # Para poder registrar quién creó la asignación
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Mostrar solo empleados activos
        self.fields['empleado'].queryset = Empleado.objects.filter(
            activo=True
        ).order_by('usuario__first_name', 'usuario__last_name')
        
        # Inicialmente, mostrar todas las viviendas o filtrar por edificio en edición
        if self.instance and self.instance.pk and self.instance.edificio:
            self.fields['edificio'].initial = self.instance.edificio
            self.fields['vivienda'].queryset = Vivienda.objects.filter(
                edificio=self.instance.edificio
            ).order_by('piso', 'numero')
        else:
            self.fields['vivienda'].queryset = Vivienda.objects.all().order_by(
                'edificio__nombre', 'piso', 'numero'
            )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:  # Solo para creación
            instance.asignado_por = self.user
        
        if commit:
            instance.save()
        return instance

class ComentarioAsignacionForm(forms.ModelForm):
    class Meta:
        model = ComentarioAsignacion
        fields = ['comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Añadir un comentario...'}),
        }

class AsignacionFiltroForm(forms.Form):
    """Formulario para filtrar las asignaciones en la vista de lista"""
    empleado = forms.ModelChoiceField(
        queryset=Empleado.objects.filter(activo=True),
        required=False,
        empty_label="Todos los empleados"
    )
    
    TIPO_CHOICES = [('', 'Todos los tipos')] + list(Asignacion.TIPOS_ASIGNACION)
    tipo = forms.ChoiceField(choices=TIPO_CHOICES, required=False)
    
    ESTADO_CHOICES = [('', 'Todos los estados')] + list(Asignacion.ESTADOS)
    estado = forms.ChoiceField(choices=ESTADO_CHOICES, required=False)
    
    edificio = forms.ModelChoiceField(
        queryset=Edificio.objects.all(),
        required=False,
        empty_label="Todos los edificios"
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )