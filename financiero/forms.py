from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import (
    ConceptoCuota, Cuota, Pago, PagoCuota, 
    CategoriaGasto, Gasto, EstadoCuenta
)
from viviendas.models import Vivienda, Residente

class ConceptoCuotaForm(forms.ModelForm):
    class Meta:
        model = ConceptoCuota
        fields = ['nombre', 'descripcion', 'monto_base', 'periodicidad', 'aplica_recargo', 'porcentaje_recargo', 'activo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases de Bootstrap
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['aplica_recargo'].widget.attrs['class'] = 'form-check-input'
        self.fields['activo'].widget.attrs['class'] = 'form-check-input'

class CuotaForm(forms.ModelForm):
    class Meta:
        model = Cuota
        fields = ['concepto', 'vivienda', 'monto', 'fecha_emision', 'fecha_vencimiento', 'notas']
        widgets = {
            'fecha_emision': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar campos
        self.fields['concepto'].queryset = ConceptoCuota.objects.filter(activo=True)
        self.fields['vivienda'].queryset = Vivienda.objects.filter(activo=True)
        # Agregar clases de Bootstrap
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Si es una cuota nueva, establecer fechas predeterminadas
        if not kwargs.get('instance'):
            self.fields['fecha_emision'].initial = timezone.now().date()
            self.fields['fecha_vencimiento'].initial = timezone.now().date() + timezone.timedelta(days=30)
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_emision = cleaned_data.get('fecha_emision')
        fecha_vencimiento = cleaned_data.get('fecha_vencimiento')
        
        if fecha_emision and fecha_vencimiento and fecha_vencimiento < fecha_emision:
            raise ValidationError({'fecha_vencimiento': _('La fecha de vencimiento debe ser posterior a la fecha de emisión.')})
        
        return cleaned_data

class GenerarCuotasForm(forms.Form):
    concepto = forms.ModelChoiceField(
        queryset=ConceptoCuota.objects.filter(activo=True),
        label="Concepto de Cuota",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    edificio = forms.ModelChoiceField(
        queryset=None,  # Se establecerá en __init__
        label="Edificio",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    viviendas = forms.ModelMultipleChoiceField(
        queryset=None,  # Se establecerá en __init__
        label="Viviendas",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': 10})
    )
    aplicar_a_todas = forms.BooleanField(
        label="Aplicar a todas las viviendas activas",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    fecha_emision = forms.DateField(
        label="Fecha de emisión",
        initial=timezone.now().date(),
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fecha_vencimiento = forms.DateField(
        label="Fecha de vencimiento",
        initial=timezone.now().date() + timezone.timedelta(days=30),
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    monto_personalizado = forms.DecimalField(
        label="Monto personalizado (opcional)",
        required=False,
        help_text="Dejar en blanco para usar el monto base del concepto",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    def __init__(self, *args, **kwargs):
        from viviendas.models import Edificio, Vivienda
        super().__init__(*args, **kwargs)
        # Configurar queryset para edificios y viviendas
        self.fields['edificio'].queryset = Edificio.objects.all()
        self.fields['viviendas'].queryset = Vivienda.objects.filter(activo=True)
    
    def clean(self):
        cleaned_data = super().clean()
        aplicar_a_todas = cleaned_data.get('aplicar_a_todas')
        viviendas = cleaned_data.get('viviendas')
        edificio = cleaned_data.get('edificio')
        fecha_emision = cleaned_data.get('fecha_emision')
        fecha_vencimiento = cleaned_data.get('fecha_vencimiento')
        
        if not aplicar_a_todas and not viviendas and not edificio:
            raise ValidationError(_('Debe seleccionar viviendas específicas, un edificio, o marcar "Aplicar a todas"'))
        
        if fecha_emision and fecha_vencimiento and fecha_vencimiento < fecha_emision:
            raise ValidationError({'fecha_vencimiento': _('La fecha de vencimiento debe ser posterior a la fecha de emisión.')})
        
        return cleaned_data

class PagoForm(forms.ModelForm):
    aplicar_a_cuotas = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = Pago
        fields = ['vivienda', 'residente', 'monto', 'fecha_pago', 'metodo_pago', 'referencia', 'comprobante', 'notas']
        widgets = {
            'fecha_pago': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        
        # Configurar campos
        self.fields['vivienda'].queryset = Vivienda.objects.filter(activo=True)
        self.fields['residente'].queryset = Residente.objects.filter(activo=True)
        
        # Agregar clases de Bootstrap
        for field_name, field in self.fields.items():
            if field_name not in ['aplicar_a_cuotas', 'comprobante']:
                field.widget.attrs['class'] = 'form-control'
        
        # Si es un pago nuevo, establecer fecha predeterminada
        if not kwargs.get('instance'):
            self.fields['fecha_pago'].initial = timezone.now().date()
        
        # Si ya tenemos una vivienda (ya sea del objeto o de los datos POST)
        vivienda_id = None
        if kwargs.get('instance'):
            vivienda_id = kwargs['instance'].vivienda_id
        elif args and 'vivienda' in args[0]:
            vivienda_id = args[0]['vivienda']
        
        if vivienda_id:
            # Obtener las cuotas pendientes para esa vivienda
            try:
                vivienda = Vivienda.objects.get(pk=vivienda_id)
                cuotas_pendientes = Cuota.objects.filter(vivienda=vivienda, pagada=False)
                choices = [(cuota.id, f"{cuota.concepto.nombre} - Vence: {cuota.fecha_vencimiento} - ${cuota.total_a_pagar()}") 
                          for cuota in cuotas_pendientes]
                self.fields['aplicar_a_cuotas'].choices = choices
                
                # Filtrar residentes de esa vivienda
                self.fields['residente'].queryset = Residente.objects.filter(vivienda=vivienda, activo=True)
            except Vivienda.DoesNotExist:
                self.fields['aplicar_a_cuotas'].choices = []
        else:
            self.fields['aplicar_a_cuotas'].choices = []
    
    def save(self, commit=True):
        pago = super().save(commit=False)
        
        if self.usuario:
            pago.registrado_por = self.usuario
        
        if commit:
            pago.save()
            
            # Aplicar el pago a las cuotas seleccionadas
            cuotas_ids = self.cleaned_data.get('aplicar_a_cuotas', [])
            if cuotas_ids:
                monto_restante = pago.monto
                for cuota_id in cuotas_ids:
                    try:
                        cuota = Cuota.objects.get(pk=cuota_id)
                        monto_aplicado = min(monto_restante, cuota.total_a_pagar())
                        if monto_aplicado > 0:
                            PagoCuota.objects.create(
                                pago=pago,
                                cuota=cuota,
                                monto_aplicado=monto_aplicado
                            )
                            monto_restante -= monto_aplicado
                    except Cuota.DoesNotExist:
                        continue
        
        return pago

class CategoriaGastoForm(forms.ModelForm):
    class Meta:
        model = CategoriaGasto
        fields = ['nombre', 'descripcion', 'presupuesto_mensual', 'color', 'activo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'color': forms.TextInput(attrs={'type': 'color'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases de Bootstrap
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['activo'].widget.attrs['class'] = 'form-check-input'

class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['categoria', 'concepto', 'descripcion', 'monto', 'fecha', 
                 'proveedor', 'factura', 'comprobante', 'estado', 'tipo_gasto', 
                 'presupuestado', 'recurrente', 'notas']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'notas': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        
        # Configurar campos
        self.fields['categoria'].queryset = CategoriaGasto.objects.filter(activo=True)
        
        # Agregar clases de Bootstrap
        for field_name, field in self.fields.items():
            if field_name not in ['comprobante', 'presupuestado', 'recurrente']:
                field.widget.attrs['class'] = 'form-control'
        
        self.fields['presupuestado'].widget.attrs['class'] = 'form-check-input'
        self.fields['recurrente'].widget.attrs['class'] = 'form-check-input'
        
        # Si es un gasto nuevo, establecer fecha predeterminada
        if not kwargs.get('instance'):
            self.fields['fecha'].initial = timezone.now().date()
    
    def save(self, commit=True):
        gasto = super().save(commit=False)
        
        if self.usuario and not gasto.registrado_por:
            gasto.registrado_por = self.usuario
        
        if commit:
            gasto.save()
        
        return gasto

class EstadoCuentaForm(forms.ModelForm):
    class Meta:
        model = EstadoCuenta
        fields = ['vivienda', 'fecha_inicio', 'fecha_fin', 'saldo_anterior']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar campos
        self.fields['vivienda'].queryset = Vivienda.objects.filter(activo=True)
        
        # Agregar clases de Bootstrap
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Si es un estado de cuenta nuevo, establecer fechas predeterminadas
        if not kwargs.get('instance'):
            hoy = timezone.now().date()
            primer_dia_mes = hoy.replace(day=1)
            ultimo_dia_mes = (primer_dia_mes + timezone.timedelta(days=32)).replace(day=1) - timezone.timedelta(days=1)
            
            self.fields['fecha_inicio'].initial = primer_dia_mes
            self.fields['fecha_fin'].initial = ultimo_dia_mes
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise ValidationError({'fecha_fin': _('La fecha de fin debe ser posterior a la fecha de inicio.')})
        
        return cleaned_data

class GenerarEstadosCuentaForm(forms.Form):
    edificio = forms.ModelChoiceField(
        queryset=None,  # Se establecerá en __init__
        label="Edificio",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    viviendas = forms.ModelMultipleChoiceField(
        queryset=None,  # Se establecerá en __init__
        label="Viviendas",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': 10})
    )
    aplicar_a_todas = forms.BooleanField(
        label="Aplicar a todas las viviendas activas",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    fecha_inicio = forms.DateField(
        label="Fecha de inicio",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fecha_fin = forms.DateField(
        label="Fecha de fin",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        from viviendas.models import Edificio, Vivienda
        super().__init__(*args, **kwargs)
        # Configurar queryset para edificios y viviendas
        self.fields['edificio'].queryset = Edificio.objects.all()
        self.fields['viviendas'].queryset = Vivienda.objects.filter(activo=True)
        
        # Configurar fechas predeterminadas
        hoy = timezone.now().date()
        primer_dia_mes = hoy.replace(day=1)
        ultimo_dia_mes = (primer_dia_mes + timezone.timedelta(days=32)).replace(day=1) - timezone.timedelta(days=1)
        
        self.fields['fecha_inicio'].initial = primer_dia_mes
        self.fields['fecha_fin'].initial = ultimo_dia_mes
    
    def clean(self):
        cleaned_data = super().clean()
        aplicar_a_todas = cleaned_data.get('aplicar_a_todas')
        viviendas = cleaned_data.get('viviendas')
        edificio = cleaned_data.get('edificio')
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if not aplicar_a_todas and not viviendas and not edificio:
            raise ValidationError(_('Debe seleccionar viviendas específicas, un edificio, o marcar "Aplicar a todas"'))
        
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise ValidationError({'fecha_fin': _('La fecha de fin debe ser posterior a la fecha de inicio.')})
        
        return cleaned_data