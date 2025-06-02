from django.contrib import admin
from django.utils.html import format_html
from .models import Visita, MovimientoResidente

@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ('nombre_visitante', 'documento_visitante', 'vivienda_destino', 'residente_autoriza', 'fecha_hora_entrada', 'fecha_hora_salida', 'estado')
    list_filter = ('fecha_hora_entrada', 'vivienda_destino__edificio', 'vivienda_destino__edificio__nombre')
    search_fields = ('nombre_visitante', 'documento_visitante', 'vivienda_destino__numero', 'residente_autoriza__usuario__first_name', 'residente_autoriza__usuario__last_name')
    date_hierarchy = 'fecha_hora_entrada'
    readonly_fields = ('fecha_hora_entrada',)
    
    fieldsets = (
        ('Información del Visitante', {
            'fields': ('nombre_visitante', 'documento_visitante', 'motivo')
        }),
        ('Destino y Autorización', {
            'fields': ('vivienda_destino', 'residente_autoriza')
        }),
        ('Control de Tiempos', {
            'fields': ('fecha_hora_entrada', 'fecha_hora_salida')
        }),
        ('Registro', {
            'fields': ('registrado_por',)
        }),
    )
    
    def estado(self, obj):
        if obj.fecha_hora_salida:
            return format_html('<span class="badge badge-success">Finalizada</span>')
        else:
            return format_html('<span class="badge badge-warning">Activa</span>')
    estado.short_description = 'Estado'
    estado.admin_order_field = 'fecha_hora_salida'

@admin.register(MovimientoResidente)
class MovimientoResidenteAdmin(admin.ModelAdmin):
    list_display = ('residente', 'tipo_movimiento', 'fecha_hora_movimiento', 'vehiculo', 'placa_vehiculo', 'edificio')
    list_filter = ('vehiculo', 'residente__vivienda__edificio')
    search_fields = ('residente__usuario__first_name', 'residente__usuario__last_name', 'placa_vehiculo', 'residente__vivienda__numero')
    
    fieldsets = (
        ('Información del Residente', {
            'fields': ('residente',)
        }),
        ('Tipo de Movimiento', {
            'fields': ('fecha_hora_entrada', 'fecha_hora_salida')
        }),
        ('Información del Vehículo', {
            'fields': ('vehiculo', 'placa_vehiculo')
        }),
    )
    
    def tipo_movimiento(self, obj):
        if obj.fecha_hora_entrada and not obj.fecha_hora_salida:
            return format_html('<span class="badge badge-success">Entrada</span>')
        elif obj.fecha_hora_salida and not obj.fecha_hora_entrada:
            return format_html('<span class="badge badge-danger">Salida</span>')
        elif obj.fecha_hora_entrada and obj.fecha_hora_salida:
            return format_html('<span class="badge badge-info">Entrada/Salida</span>')
        else:
            return format_html('<span class="badge badge-secondary">N/A</span>')
    tipo_movimiento.short_description = 'Tipo'
    tipo_movimiento.admin_order_field = 'fecha_hora_entrada'
    
    def fecha_hora_movimiento(self, obj):
        if obj.fecha_hora_entrada and not obj.fecha_hora_salida:
            return obj.fecha_hora_entrada.strftime('%d/%m/%Y %H:%M')
        elif obj.fecha_hora_salida and not obj.fecha_hora_entrada:
            return obj.fecha_hora_salida.strftime('%d/%m/%Y %H:%M')
        elif obj.fecha_hora_entrada and obj.fecha_hora_salida:
            return f"E: {obj.fecha_hora_entrada.strftime('%d/%m/%Y %H:%M')} | S: {obj.fecha_hora_salida.strftime('%d/%m/%Y %H:%M')}"
        else:
            return "N/A"
    fecha_hora_movimiento.short_description = 'Fecha/Hora'
    fecha_hora_movimiento.admin_order_field = 'fecha_hora_entrada'
    
    def edificio(self, obj):
        if obj.residente and obj.residente.vivienda:
            return obj.residente.vivienda.edificio.nombre
        return "N/A"
    edificio.short_description = 'Edificio'
    edificio.admin_order_field = 'residente__vivienda__edificio__nombre'