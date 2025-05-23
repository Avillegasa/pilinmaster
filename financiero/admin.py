from django.contrib import admin
from .models import (
    ConceptoCuota, Cuota, Pago, PagoCuota, 
    CategoriaGasto, Gasto, EstadoCuenta
)

@admin.register(ConceptoCuota)
class ConceptoCuotaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'monto_base', 'periodicidad', 'aplica_recargo', 'porcentaje_recargo', 'activo')
    list_filter = ('periodicidad', 'aplica_recargo', 'activo')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activo',)
    fieldsets = (
        (None, {
            'fields': ('nombre', 'descripcion', 'monto_base', 'periodicidad')
        }),
        ('Configuración de Recargos', {
            'fields': ('aplica_recargo', 'porcentaje_recargo'),
            'classes': ('collapse',),
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )

class PagoCuotaInline(admin.TabularInline):
    model = PagoCuota
    extra = 1
    raw_id_fields = ('cuota',)

@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    list_display = ('concepto', 'vivienda', 'monto', 'fecha_emision', 'fecha_vencimiento', 'pagada', 'recargo', 'total_a_pagar')
    list_filter = ('pagada', 'concepto', 'fecha_emision', 'fecha_vencimiento')
    search_fields = ('vivienda__numero', 'concepto__nombre')
    raw_id_fields = ('vivienda',)
    date_hierarchy = 'fecha_vencimiento'
    readonly_fields = ('total_a_pagar',)
    
    def total_a_pagar(self, obj):
        return obj.total_a_pagar()
    total_a_pagar.short_description = 'Total a Pagar'
    
    fieldsets = (
        (None, {
            'fields': ('concepto', 'vivienda', 'monto')
        }),
        ('Fechas', {
            'fields': ('fecha_emision', 'fecha_vencimiento')
        }),
        ('Estado', {
            'fields': ('pagada', 'recargo', 'total_a_pagar')
        }),
        ('Información Adicional', {
            'fields': ('notas',),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['actualizar_recargos']
    
    def actualizar_recargos(self, request, queryset):
        for cuota in queryset:
            cuota.actualizar_recargo()
        self.message_user(request, f"Se actualizaron los recargos para {queryset.count()} cuotas.")
    actualizar_recargos.short_description = "Actualizar recargos para las cuotas seleccionadas"

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('vivienda', 'residente', 'monto', 'fecha_pago', 'metodo_pago', 'estado', 'referencia')
    list_filter = ('estado', 'metodo_pago', 'fecha_pago')
    search_fields = ('vivienda__numero', 'residente__usuario__first_name', 'residente__usuario__last_name', 'referencia')
    raw_id_fields = ('vivienda', 'residente')
    date_hierarchy = 'fecha_pago'
    readonly_fields = ('fecha_verificacion',)
    
    fieldsets = (
        (None, {
            'fields': ('vivienda', 'residente', 'monto', 'fecha_pago')
        }),
        ('Detalles del Pago', {
            'fields': ('metodo_pago', 'referencia', 'comprobante')
        }),
        ('Estado y Verificación', {
            'fields': ('estado', 'verificado_por', 'fecha_verificacion')
        }),
        ('Información Adicional', {
            'fields': ('registrado_por', 'notas'),
            'classes': ('collapse',),
        }),
    )
    
    inlines = [PagoCuotaInline]
    
    actions = ['verificar_pagos', 'rechazar_pagos']
    
    def verificar_pagos(self, request, queryset):
        for pago in queryset.filter(estado='PENDIENTE'):
            pago.verificar_pago(request.user)
        self.message_user(request, f"Se verificaron {queryset.filter(estado='PENDIENTE').count()} pagos.")
    verificar_pagos.short_description = "Verificar pagos seleccionados"
    
    def rechazar_pagos(self, request, queryset):
        for pago in queryset.filter(estado='PENDIENTE'):
            pago.rechazar_pago(request.user, "Rechazado en administración")
        self.message_user(request, f"Se rechazaron {queryset.filter(estado='PENDIENTE').count()} pagos.")
    rechazar_pagos.short_description = "Rechazar pagos seleccionados"

@admin.register(CategoriaGasto)
class CategoriaGastoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'presupuesto_mensual', 'total_gastado_mes_actual', 'porcentaje_presupuesto_utilizado', 'color', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')
    list_editable = ('presupuesto_mensual', 'color', 'activo')
    
    def total_gastado_mes_actual(self, obj):
        return f"${obj.total_gastado_mes_actual()}"
    total_gastado_mes_actual.short_description = 'Gastado (Mes Actual)'
    
    def porcentaje_presupuesto_utilizado(self, obj):
        porcentaje = obj.porcentaje_presupuesto_utilizado()
        return f"{porcentaje:.1f}%"
    porcentaje_presupuesto_utilizado.short_description = '% Utilizado'

@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('concepto', 'categoria', 'monto', 'fecha', 'estado', 'tipo_gasto', 'proveedor')
    list_filter = ('estado', 'tipo_gasto', 'categoria', 'fecha', 'presupuestado', 'recurrente')
    search_fields = ('concepto', 'descripcion', 'proveedor', 'factura')
    raw_id_fields = ('registrado_por', 'autorizado_por')
    date_hierarchy = 'fecha'
    
    fieldsets = (
        (None, {
            'fields': ('concepto', 'descripcion', 'monto', 'categoria')
        }),
        ('Detalles del Gasto', {
            'fields': ('tipo_gasto', 'proveedor', 'factura', 'comprobante')
        }),
        ('Fechas y Estado', {
            'fields': ('fecha', 'fecha_pago', 'estado')
        }),
        ('Autorización', {
            'fields': ('registrado_por', 'autorizado_por')
        }),
        ('Clasificación', {
            'fields': ('presupuestado', 'recurrente'),
            'classes': ('collapse',),
        }),
        ('Información Adicional', {
            'fields': ('notas',),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['marcar_como_pagados', 'cancelar_gastos']
    
    def marcar_como_pagados(self, request, queryset):
        for gasto in queryset.filter(estado='PENDIENTE'):
            gasto.marcar_como_pagado()
        self.message_user(request, f"Se marcaron {queryset.filter(estado='PENDIENTE').count()} gastos como pagados.")
    marcar_como_pagados.short_description = "Marcar gastos seleccionados como pagados"
    
    def cancelar_gastos(self, request, queryset):
        for gasto in queryset.filter(estado='PENDIENTE'):
            gasto.cancelar()
        self.message_user(request, f"Se cancelaron {queryset.filter(estado='PENDIENTE').count()} gastos.")
    cancelar_gastos.short_description = "Cancelar gastos seleccionados"

@admin.register(EstadoCuenta)
class EstadoCuentaAdmin(admin.ModelAdmin):
    list_display = ('vivienda', 'fecha_inicio', 'fecha_fin', 'saldo_anterior', 'total_cuotas', 'total_pagos', 'saldo_final', 'enviado')
    list_filter = ('enviado', 'fecha_generacion', 'fecha_inicio', 'fecha_fin')
    search_fields = ('vivienda__numero',)
    raw_id_fields = ('vivienda',)
    date_hierarchy = 'fecha_fin'
    readonly_fields = ('fecha_generacion', 'fecha_envio')
    
    fieldsets = (
        (None, {
            'fields': ('vivienda', 'fecha_inicio', 'fecha_fin')
        }),
        ('Saldos', {
            'fields': ('saldo_anterior', 'total_cuotas', 'total_recargos', 'total_pagos', 'saldo_final')
        }),
        ('Estado de Envío', {
            'fields': ('enviado', 'fecha_envio', 'pdf_generado')
        }),
        ('Metadata', {
            'fields': ('fecha_generacion',),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['generar_pdfs', 'marcar_como_enviados', 'recalcular_totales']
    
    def generar_pdfs(self, request, queryset):
        for estado in queryset:
            estado.generar_pdf()
        self.message_user(request, f"Se generaron PDFs para {queryset.count()} estados de cuenta.")
    generar_pdfs.short_description = "Generar PDFs para estados de cuenta seleccionados"
    
    def marcar_como_enviados(self, request, queryset):
        for estado in queryset.filter(enviado=False):
            estado.marcar_como_enviado()
        self.message_user(request, f"Se marcaron {queryset.filter(enviado=False).count()} estados de cuenta como enviados.")
    marcar_como_enviados.short_description = "Marcar estados de cuenta como enviados"
    
    def recalcular_totales(self, request, queryset):
        for estado in queryset:
            estado.calcular_totales()
        self.message_user(request, f"Se recalcularon los totales para {queryset.count()} estados de cuenta.")
    recalcular_totales.short_description = "Recalcular totales para estados de cuenta seleccionados"