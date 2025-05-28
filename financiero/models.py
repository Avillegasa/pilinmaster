from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from usuarios.models import Usuario
from viviendas.models import Vivienda, Residente

class ConceptoCuota(models.Model):
    """
    Modelo para definir los diferentes conceptos de cuotas
    Ejemplos: Cuota ordinaria, Cuota extraordinaria, Fondo de reserva, etc.
    """
    PERIODICIDAD_CHOICES = [
        ('MENSUAL', 'Mensual'),
        ('BIMESTRAL', 'Bimestral'),
        ('TRIMESTRAL', 'Trimestral'),
        ('SEMESTRAL', 'Semestral'),
        ('ANUAL', 'Anual'),
        ('UNICA', 'Única vez'),
    ]
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    monto_base = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    periodicidad = models.CharField(max_length=15, choices=PERIODICIDAD_CHOICES, default='MENSUAL')
    aplica_recargo = models.BooleanField(default=True, help_text="Indica si se aplican recargos por mora")
    porcentaje_recargo = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)],
                                           help_text="Porcentaje de recargo mensual por pago tardío")
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.get_periodicidad_display()}"
    
    class Meta:
        verbose_name = "Concepto de Cuota"
        verbose_name_plural = "Conceptos de Cuotas"
        ordering = ['nombre']

class Cuota(models.Model):
    """
    Modelo para las cuotas asignadas a cada vivienda
    """
    concepto = models.ForeignKey(ConceptoCuota, on_delete=models.PROTECT, related_name='cuotas')
    vivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE, related_name='cuotas')
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    fecha_emision = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField()
    pagada = models.BooleanField(default=False)
    recargo = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    notas = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.concepto.nombre} - {self.vivienda} - {self.fecha_vencimiento}"
    
    def calcular_recargo(self):
        """Calcula el recargo si la cuota está vencida y aplica recargo"""
        if not self.pagada and self.concepto.aplica_recargo and timezone.now().date() > self.fecha_vencimiento:
            # Calcular meses de retraso
            hoy = timezone.now().date()
            meses_retraso = (hoy.year - self.fecha_vencimiento.year) * 12 + (hoy.month - self.fecha_vencimiento.month)
            if hoy.day < self.fecha_vencimiento.day:
                meses_retraso -= 1
            
            # Asegurar que al menos hay un mes de retraso
            meses_retraso = max(1, meses_retraso)
            
            # Calcular recargo acumulado con precisión decimal
            porcentaje_recargo_mensual = self.concepto.porcentaje_recargo / 100
            recargo_acumulado = self.monto * porcentaje_recargo_mensual * meses_retraso
            
            # Redondear a 2 decimales para evitar errores de precisión
            from decimal import Decimal, ROUND_HALF_UP
            return recargo_acumulado.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return Decimal('0.00')

    
    def actualizar_recargo(self):
        """Actualiza el campo recargo según el cálculo actual"""
        nuevo_recargo = self.calcular_recargo()
        if nuevo_recargo != self.recargo:
            self.recargo = nuevo_recargo
            self.save(update_fields=['recargo'])
    
    def total_a_pagar(self):
        """Devuelve el monto total a pagar incluyendo recargos"""
        return self.monto + self.recargo
    
    def marcar_como_pagada(self):
        """Marca la cuota como pagada y elimina recargos"""
        self.pagada = True
        self.recargo = 0
        self.save()
    
    def clean(self):
        # Validar que la fecha de vencimiento sea posterior a la fecha de emisión
        if self.fecha_vencimiento and self.fecha_emision and self.fecha_vencimiento < self.fecha_emision:
            raise ValidationError({'fecha_vencimiento': _('La fecha de vencimiento debe ser posterior a la fecha de emisión.')})
    
    def save(self, *args, **kwargs):
        # Validación adicional al guardar
        self.full_clean()
        
        # Para cuotas nuevas, asignar el monto base del concepto si no se especifica otro
        if not self.pk and self.monto == 0:
            self.monto = self.concepto.monto_base
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Cuota"
        verbose_name_plural = "Cuotas"
        ordering = ['-fecha_vencimiento']
        indexes = [
            models.Index(fields=['vivienda', 'pagada']),
            models.Index(fields=['fecha_vencimiento']),
        ]

class Pago(models.Model):
    """
    Modelo para registrar pagos realizados por los residentes
    """
    METODO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia Bancaria'),
        ('CHEQUE', 'Cheque'),
        ('TARJETA', 'Tarjeta de Crédito/Débito'),
        ('OTRO', 'Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de verificación'),
        ('VERIFICADO', 'Verificado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    
    vivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE, related_name='pagos')
    residente = models.ForeignKey(Residente, on_delete=models.SET_NULL, null=True, blank=True, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    fecha_pago = models.DateField(default=timezone.now)
    metodo_pago = models.CharField(max_length=15, choices=METODO_PAGO_CHOICES)
    referencia = models.CharField(max_length=100, blank=True, help_text="Número de referencia, cheque o transacción")
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='PENDIENTE')
    comprobante = models.FileField(upload_to='pagos/comprobantes/', null=True, blank=True)
    notas = models.TextField(blank=True)
    registrado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='pagos_registrados')
    verificado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='pagos_verificados')
    fecha_verificacion = models.DateTimeField(null=True, blank=True)
    
    # Relación muchos a muchos con Cuota a través de PagoCuota
    cuotas = models.ManyToManyField(Cuota, through='PagoCuota', related_name='pagos')
    
    def __str__(self):
        return f"{self.vivienda} - ${self.monto} - {self.fecha_pago}"
    
    def verificar_pago(self, usuario):
        """Verifica el pago y actualiza el estado"""
        self.estado = 'VERIFICADO'
        self.verificado_por = usuario
        self.fecha_verificacion = timezone.now()
        self.save()
    
    def rechazar_pago(self, usuario, motivo=None):
        """Rechaza el pago y actualiza el estado"""
        self.estado = 'RECHAZADO'
        self.verificado_por = usuario
        self.fecha_verificacion = timezone.now()
        if motivo:
            self.notas = f"{self.notas}\nRechazado: {motivo}".strip()
        self.save()
        
        # Desmarcar las cuotas como pagadas
        for pago_cuota in self.pagocuota_set.all():
            cuota = pago_cuota.cuota
            cuota.pagada = False
            cuota.save()
    
    def get_cuotas_pendientes(self):
        """Devuelve las cuotas pendientes de la vivienda"""
        return Cuota.objects.filter(vivienda=self.vivienda, pagada=False).order_by('fecha_vencimiento')
    
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-fecha_pago', '-id']
        indexes = [
            models.Index(fields=['vivienda', 'estado']),
            models.Index(fields=['fecha_pago']),
        ]

class PagoCuota(models.Model):
    """
    Modelo intermedio para relacionar pagos con cuotas específicas
    """
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE)
    cuota = models.ForeignKey(Cuota, on_delete=models.CASCADE)
    monto_aplicado = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    def __str__(self):
        return f"{self.pago} - {self.cuota}"
    
    def clean(self):
        # Validar que el monto aplicado no exceda el total de la cuota
        if self.monto_aplicado > self.cuota.total_a_pagar():
            raise ValidationError({'monto_aplicado': _('El monto aplicado no puede exceder el total a pagar de la cuota.')})
        
    class Meta:
        verbose_name = "Detalle Pago-Cuota"
        verbose_name_plural = "Detalles Pago-Cuota"
        unique_together = ('pago', 'cuota')

class CategoriaGasto(models.Model):
    """
    Modelo para categorizar los gastos del condominio
    """
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    presupuesto_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    color = models.CharField(max_length=7, default="#3498db", help_text="Código de color HEX para gráficos")
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre
    
    def total_gastado_mes_actual(self):
        """Calcula el total gastado en esta categoría en el mes actual"""
        hoy = timezone.now().date()
        primer_dia_mes = hoy.replace(day=1)
        return Gasto.objects.filter(
            categoria=self,
            fecha__gte=primer_dia_mes,
            fecha__lte=hoy
        ).aggregate(total=models.Sum('monto'))['total'] or 0
    
    def porcentaje_presupuesto_utilizado(self):
        """Calcula el porcentaje del presupuesto utilizado en el mes actual"""
        if self.presupuesto_mensual == 0:
            return 0
        
        gastado = self.total_gastado_mes_actual()
        return (gastado / self.presupuesto_mensual) * 100
    
    class Meta:
        verbose_name = "Categoría de Gasto"
        verbose_name_plural = "Categorías de Gastos"
        ordering = ['nombre']

class Gasto(models.Model):
    """
    Modelo para registrar los gastos del condominio
    """
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de pago'),
        ('PAGADO', 'Pagado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    TIPO_GASTO_CHOICES = [
        ('ORDINARIO', 'Gasto Ordinario'),
        ('EXTRAORDINARIO', 'Gasto Extraordinario'),
        ('MANTENIMIENTO', 'Mantenimiento'),
        ('SERVICIO', 'Servicio'),
        ('OTRO', 'Otro'),
    ]
    
    categoria = models.ForeignKey(CategoriaGasto, on_delete=models.PROTECT, related_name='gastos')
    concepto = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    fecha = models.DateField(default=timezone.now)
    fecha_pago = models.DateField(null=True, blank=True)
    proveedor = models.CharField(max_length=200, blank=True)
    comprobante = models.FileField(upload_to='gastos/comprobantes/', null=True, blank=True)
    factura = models.CharField(max_length=100, blank=True, help_text="Número de factura o recibo")
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='PENDIENTE')
    tipo_gasto = models.CharField(max_length=15, choices=TIPO_GASTO_CHOICES, default='ORDINARIO')
    registrado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='gastos_registrados')
    autorizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='gastos_autorizados')
    notas = models.TextField(blank=True)
    
    # Campos para manejo de presupuestos
    presupuestado = models.BooleanField(default=False, help_text="Indica si el gasto estaba presupuestado")
    recurrente = models.BooleanField(default=False, help_text="Indica si es un gasto que se repite periódicamente")
    
    def __str__(self):
        return f"{self.concepto} - ${self.monto} - {self.fecha}"
    
    def marcar_como_pagado(self, fecha_pago=None):
        """Marca el gasto como pagado"""
        self.estado = 'PAGADO'
        self.fecha_pago = fecha_pago or timezone.now().date()
        self.save()
    
    def cancelar(self):
        """Cancela el gasto"""
        self.estado = 'CANCELADO'
        self.save()
    
    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        ordering = ['-fecha', '-id']
        indexes = [
            models.Index(fields=['categoria', 'fecha']),
            models.Index(fields=['estado']),
        ]

class EstadoCuenta(models.Model):
    """
    Modelo para generar y almacenar estados de cuenta por vivienda y período
    """
    vivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE, related_name='estados_cuenta')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    saldo_anterior = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cuotas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_pagos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_recargos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo_final = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    enviado = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    pdf_generado = models.FileField(upload_to='estados_cuenta/', null=True, blank=True)
    
    def __str__(self):
        return f"Estado de Cuenta - {self.vivienda} - {self.fecha_inicio} a {self.fecha_fin}"
    
    def calcular_totales(self):
        """
        Calcula todos los totales y saldos para el estado de cuenta
        """
        # Obtener cuotas en el período
        cuotas_periodo = Cuota.objects.filter(
            vivienda=self.vivienda,
            fecha_emision__gte=self.fecha_inicio,
            fecha_emision__lte=self.fecha_fin
        )
        
        # Obtener pagos en el período
        pagos_periodo = Pago.objects.filter(
            vivienda=self.vivienda,
            fecha_pago__gte=self.fecha_inicio,
            fecha_pago__lte=self.fecha_fin,
            estado='VERIFICADO'
        )
        
        # Calcular totales
        self.total_cuotas = cuotas_periodo.aggregate(total=models.Sum('monto'))['total'] or 0
        self.total_pagos = pagos_periodo.aggregate(total=models.Sum('monto'))['total'] or 0
        self.total_recargos = cuotas_periodo.aggregate(total=models.Sum('recargo'))['total'] or 0
        
        # Calcular saldo final
        self.saldo_final = self.saldo_anterior + self.total_cuotas + self.total_recargos - self.total_pagos
        
        # Guardar sin desencadenar el cálculo de nuevo
        super(EstadoCuenta, self).save()
    
    def obtener_detalle_cuotas(self):
        """
        Devuelve el detalle de cuotas incluidas en este estado de cuenta
        """
        return Cuota.objects.filter(
            vivienda=self.vivienda,
            fecha_emision__gte=self.fecha_inicio,
            fecha_emision__lte=self.fecha_fin
        ).order_by('fecha_emision')
    
    def obtener_detalle_pagos(self):
        """
        Devuelve el detalle de pagos incluidos en este estado de cuenta
        """
        return Pago.objects.filter(
            vivienda=self.vivienda,
            fecha_pago__gte=self.fecha_inicio,
            fecha_pago__lte=self.fecha_fin,
            estado='VERIFICADO'
        ).order_by('fecha_pago')
    
    def marcar_como_enviado(self):
        """
        Marca el estado de cuenta como enviado y registra la fecha
        """
        self.enviado = True
        self.fecha_envio = timezone.now()
        self.save()
    
    def generar_pdf(self):
        """
        Genera un PDF del estado de cuenta
        La implementación real dependerá de la biblioteca PDF que se use
        """
        # Esta función sería implementada con una biblioteca como reportlab o weasyprint
        pass
    
    def save(self, *args, **kwargs):
        # Validación para asegurar que fecha_fin es posterior a fecha_inicio
        if self.fecha_fin < self.fecha_inicio:
            raise ValidationError({'fecha_fin': _('La fecha de fin debe ser posterior a la fecha de inicio.')})
        
        # Crear estado de cuenta por primera vez
        is_new = self.pk is None
        
        # Guardar primero para tener un ID
        super(EstadoCuenta, self).save(*args, **kwargs)
        
        # Calcular totales si es nuevo
        if is_new:
            self.calcular_totales()
    
    class Meta:
        verbose_name = "Estado de Cuenta"
        verbose_name_plural = "Estados de Cuenta"
        ordering = ['-fecha_fin', 'vivienda']
        unique_together = ('vivienda', 'fecha_inicio', 'fecha_fin')
        indexes = [
            models.Index(fields=['vivienda', 'fecha_fin']),
        ]

# Señales y hooks

@receiver(post_save, sender=PagoCuota)
def actualizar_cuota_al_pagar(sender, instance, created, **kwargs):
    """
    Cuando se crea o actualiza un PagoCuota, actualiza el estado de la cuota
    """
    cuota = instance.cuota
    
    # Si el pago está verificado, marcar la cuota como pagada
    if instance.pago.estado == 'VERIFICADO':
        # Verificar si el monto aplicado cubre el total
        if instance.monto_aplicado >= cuota.total_a_pagar():
            cuota.pagada = True
            cuota.recargo = 0
        else:
            # Pago parcial, reducir el monto pendiente
            cuota.monto = cuota.monto - instance.monto_aplicado
            cuota.pagada = False
        
        cuota.save()

@receiver(post_delete, sender=PagoCuota)
def revertir_pago_al_eliminar(sender, instance, **kwargs):
    """
    Cuando se elimina un PagoCuota, revierte el estado de la cuota si es necesario
    """
    cuota = instance.cuota
    
    # Si la cuota estaba marcada como pagada y el pago estaba verificado
    if cuota.pagada and instance.pago.estado == 'VERIFICADO':
        # Restaurar el estado de la cuota
        cuota.pagada = False
        cuota.actualizar_recargo()  # Recalcular recargos
        cuota.save()