from django.contrib import admin
from .models import Visita, MovimientoResidente

class VisitaAdmin(admin.ModelAdmin):
    list_display = ('nombre_visitante', 'documento_visitante', 'vivienda_destino', 'residente_autoriza', 'fecha_hora_entrada', 'fecha_hora_salida', 'estado')
    list_filter = ('fecha_hora_entrada', 'vivienda_destino__edificio')
    search_fields = ('nombre_visitante', 'documento_visitante', 'vivienda_destino__numero')
    date_hierarchy = 'fecha_hora_entrada'
    
    def estado(self, obj):
        return "Finalizada" if obj.fecha_hora_salida else "Activa"
    estado.short_description = 'Estado'

class MovimientoResidenteAdmin(admin.ModelAdmin):
    list_display = ('residente', 'tipo_movimiento', 'fecha_hora', 'vehiculo', 'placa_vehiculo')
    list_filter = ('fecha_hora_entrada', 'fecha_hora_salida', 'residente__vivienda__edificio', 'vehiculo')
    search_fields = ('residente__usuario__first_name', 'residente__usuario__last_name', 'placa_vehiculo')
    
    def tipo_movimiento(self, obj):
        if obj.fecha_hora_entrada and not obj.fecha_hora_salida:
            return "Entrada"
        elif obj.fecha_hora_salida and not obj.fecha_hora_entrada:
            return "Salida"
        return "N/A"
    tipo_movimiento.short_description = 'Tipo'
    
    def fecha_hora(self, obj):
        if obj.fecha_hora_entrada and not obj.fecha_hora_salida:
            return obj.fecha_hora_entrada
        elif obj.fecha_hora_salida and not obj.fecha_hora_entrada:
            return obj.fecha_hora_salida
        return None
    fecha_hora.short_description = 'Fecha/Hora'

admin.site.register(Visita, VisitaAdmin)
admin.site.register(MovimientoResidente, MovimientoResidenteAdmin)
