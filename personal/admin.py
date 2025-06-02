from django.contrib import admin
from .models import Puesto, Empleado, Asignacion, ComentarioAsignacion

class ComentarioAsignacionInline(admin.TabularInline):
    model = ComentarioAsignacion
    extra = 0
    readonly_fields = ['fecha']

class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('get_nombre_completo', 'puesto', 'fecha_contratacion', 'tipo_contrato', 'activo')
    list_filter = ('puesto', 'tipo_contrato', 'activo')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'puesto__nombre')
    date_hierarchy = 'fecha_contratacion'
    
    def get_nombre_completo(self, obj):
        return f"{obj.usuario.first_name} {obj.usuario.last_name}"
    get_nombre_completo.short_description = 'Nombre'

class AsignacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'empleado', 'tipo', 'fecha_asignacion', 'fecha_inicio', 'estado', 'prioridad')
    list_filter = ('estado', 'tipo', 'prioridad', 'empleado__puesto')
    search_fields = ('titulo', 'descripcion', 'empleado__usuario__first_name', 'empleado__usuario__last_name')
    date_hierarchy = 'fecha_asignacion'
    inlines = [ComentarioAsignacionInline]

class PuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'requiere_especializacion', 'empleados_count')
    list_filter = ('requiere_especializacion',)
    search_fields = ('nombre', 'descripcion')
    
    def empleados_count(self, obj):
        return obj.empleados.count()
    empleados_count.short_description = 'Empleados'

class ComentarioAsignacionAdmin(admin.ModelAdmin):
    list_display = ('asignacion', 'usuario', 'fecha')
    list_filter = ('fecha', 'usuario')
    search_fields = ('comentario', 'asignacion__titulo', 'usuario__username')
    date_hierarchy = 'fecha'
    readonly_fields = ['fecha']

# Registrar los modelos en el admin
admin.site.register(Puesto, PuestoAdmin)
admin.site.register(Empleado, EmpleadoAdmin)
admin.site.register(Asignacion, AsignacionAdmin)
admin.site.register(ComentarioAsignacion, ComentarioAsignacionAdmin)