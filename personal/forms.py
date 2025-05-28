from django import forms
from django.core.exceptions import ValidationError
from .models import Puesto, Empleado, Asignacion, ComentarioAsignacion
from usuarios.models import Usuario, Rol
from viviendas.models import Edificio, Vivienda

class PuestoForm(forms.ModelForm):
    class Meta:
        model = Puesto
        fields = '__all__'
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
    
    # ✅ CORRECCIÓN: Validación personalizada agregada
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            nombre = nombre.strip().title()
            # Verificar duplicados excluyendo la instancia actual
            existing = Puesto.objects.filter(nombre__iexact=nombre)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError('Ya existe un puesto con este nombre.')
            
            return nombre
        return nombre

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
            'salario': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'contacto_emergencia': forms.TextInput(attrs={'placeholder': 'Nombre del contacto de emergencia'}),
            'telefono_emergencia': forms.TextInput(attrs={'placeholder': '+1234567890'}),
            'especialidad': forms.TextInput(attrs={'placeholder': 'Ej: Electricidad, Plomería, etc.'}),
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
        ).filter(is_active=True).order_by('first_name', 'last_name')
        
        # ✅ CORRECCIÓN: Mejorar labels y help_text
        self.fields['usuario'].label = 'Usuario del Sistema'
        self.fields['usuario'].help_text = 'Seleccione el usuario que será empleado'
        self.fields['salario'].help_text = 'Salario mensual en moneda local'
        self.fields['fecha_contratacion'].help_text = 'Fecha en que inició labores'
        
        # Hacer campos opcionales más claros
        self.fields['salario'].required = False
        self.fields['contacto_emergencia'].required = False
        self.fields['telefono_emergencia'].required = False
        self.fields['especialidad'].required = False
    
    # ✅ CORRECCIÓN: Validaciones personalizadas agregadas
    def clean_salario(self):
        salario = self.cleaned_data.get('salario')
        if salario is not None and salario < 0:
            raise ValidationError('El salario no puede ser negativo.')
        return salario
    
    def clean_telefono_emergencia(self):
        telefono = self.cleaned_data.get('telefono_emergencia')
        if telefono:
            # Limpiar el teléfono de espacios y caracteres especiales
            telefono = ''.join(c for c in telefono if c.isdigit() or c in ['+', '-', ' ', '(', ')'])
            if len(telefono.replace(' ', '').replace('+', '').replace('-', '').replace('(', '').replace(')', '')) < 8:
                raise ValidationError('El teléfono de emergencia debe tener al menos 8 dígitos.')
        return telefono
    
    def clean(self):
        cleaned_data = super().clean()
        contacto_emergencia = cleaned_data.get('contacto_emergencia')
        telefono_emergencia = cleaned_data.get('telefono_emergencia')
        
        # Si se proporciona uno, se debe proporcionar el otro
        if contacto_emergencia and not telefono_emergencia:
            raise ValidationError('Si proporciona un contacto de emergencia, debe incluir el teléfono.')
        if telefono_emergencia and not contacto_emergencia:
            raise ValidationError('Si proporciona un teléfono de emergencia, debe incluir el nombre del contacto.')
        
        return cleaned_data

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
            'descripcion': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describa detalladamente la asignación...'}),
            'notas': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Notas adicionales (opcional)...'}),
            'titulo': forms.TextInput(attrs={'placeholder': 'Título descriptivo de la asignación'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Para poder registrar quién creó la asignación
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Mostrar solo empleados activos
        self.fields['empleado'].queryset = Empleado.objects.filter(
            activo=True
        ).select_related('usuario', 'puesto').order_by('usuario__first_name', 'usuario__last_name')
        
        # Inicialmente, mostrar todas las viviendas o filtrar por edificio en edición
        if self.instance and self.instance.pk and self.instance.edificio:
            self.fields['edificio'].initial = self.instance.edificio
            self.fields['vivienda'].queryset = Vivienda.objects.filter(
                edificio=self.instance.edificio, activo=True
            ).order_by('piso', 'numero')
        else:
            self.fields['vivienda'].queryset = Vivienda.objects.filter(
                activo=True
            ).select_related('edificio').order_by('edificio__nombre', 'piso', 'numero')
        
        # ✅ CORRECCIÓN: Mejorar labels y help_text
        self.fields['empleado'].label = 'Empleado Asignado'
        self.fields['tipo'].help_text = 'Tarea puntual: se completa una vez. Responsabilidad: trabajo continuo.'
        self.fields['fecha_inicio'].help_text = 'Fecha en que debe comenzar la asignación'
        self.fields['fecha_fin'].help_text = 'Fecha límite (opcional para responsabilidades recurrentes)'
        self.fields['prioridad'].help_text = 'Nivel de urgencia de la asignación'
        
        # Configurar el campo vivienda
        self.fields['vivienda'].required = False
        self.fields['vivienda'].help_text = 'Vivienda específica (opcional si aplica a todo el edificio)'
    
    # ✅ CORRECCIÓN: Validaciones personalizadas agregadas
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        tipo = cleaned_data.get('tipo')
        edificio = cleaned_data.get('edificio')
        vivienda = cleaned_data.get('vivienda')
        
        # Validar fechas
        if fecha_inicio and fecha_fin:
            if fecha_inicio > fecha_fin:
                raise ValidationError('La fecha de inicio no puede ser posterior a la fecha de fin.')
        
        # Para tareas puntuales, requerir fecha de fin
        if tipo == 'TAREA' and not fecha_fin:
            raise ValidationError('Las tareas puntuales deben tener una fecha de finalización.')
        
        # Si se selecciona vivienda, debe haber un edificio
        if vivienda and not edificio:
            cleaned_data['edificio'] = vivienda.edificio
        
        # Si se selecciona vivienda, verificar que pertenezca al edificio
        if vivienda and edificio and vivienda.edificio != edificio:
            raise ValidationError('La vivienda seleccionada no pertenece al edificio especificado.')
        
        return cleaned_data
    
    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        if titulo:
            titulo = titulo.strip()
            if len(titulo) < 5:
                raise ValidationError('El título debe tener al menos 5 caracteres.')
        return titulo
    
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
            'comentario': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Añadir un comentario...',
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comentario'].label = 'Comentario'
        self.fields['comentario'].help_text = 'Comparte actualizaciones, notas o preguntas sobre esta asignación'
    
    # ✅ CORRECCIÓN: Validación agregada
    def clean_comentario(self):
        comentario = self.cleaned_data.get('comentario')
        if comentario:
            comentario = comentario.strip()
            if len(comentario) < 3:
                raise ValidationError('El comentario debe tener al menos 3 caracteres.')
            if len(comentario) > 1000:
                raise ValidationError('El comentario no puede exceder 1000 caracteres.')
        return comentario

class AsignacionFiltroForm(forms.Form):
    """Formulario para filtrar las asignaciones en la vista de lista"""
    empleado = forms.ModelChoiceField(
        queryset=Empleado.objects.filter(activo=True).select_related('usuario', 'puesto'),
        required=False,
        empty_label="Todos los empleados",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    TIPO_CHOICES = [('', 'Todos los tipos')] + list(Asignacion.TIPOS_ASIGNACION)
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES, 
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    ESTADO_CHOICES = [('', 'Todos los estados')] + list(Asignacion.ESTADOS)
    estado = forms.ChoiceField(
        choices=ESTADO_CHOICES, 
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    edificio = forms.ModelChoiceField(
        queryset=Edificio.objects.all().order_by('nombre'),
        required=False,
        empty_label="Todos los edificios",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Fecha desde',
        help_text='Filtrar asignaciones desde esta fecha'
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Fecha hasta',
        help_text='Filtrar asignaciones hasta esta fecha'
    )
    
    # ✅ CORRECCIÓN: Validación de fechas agregada
    def clean(self):
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get('fecha_desde')
        fecha_hasta = cleaned_data.get('fecha_hasta')
        
        if fecha_desde and fecha_hasta:
            if fecha_desde > fecha_hasta:
                raise ValidationError('La fecha desde no puede ser posterior a la fecha hasta.')
        
        return cleaned_data