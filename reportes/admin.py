from django.contrib import admin
from .models import Reporte

class ReporteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'fecha_creacion', 'fecha_desde', 'fecha_hasta', 'creado_por', 'tiene_archivo')
    list_filter = ('tipo', 'fecha_creacion')
    search_fields = ('nombre', 'creado_por__username')
    date_hierarchy = 'fecha_creacion'
    
    def tiene_archivo(self, obj):
        return bool(obj.archivo)
    tiene_archivo.boolean = True
    tiene_archivo.short_description = 'Archivo'

admin.site.register(Reporte, ReporteAdmin)