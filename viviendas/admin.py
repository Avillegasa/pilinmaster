from django.contrib import admin
from .models import Edificio, Vivienda, Residente

class ViviendaInline(admin.TabularInline):
    model = Vivienda
    extra = 0

class EdificioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'pisos', 'total_viviendas')
    search_fields = ('nombre', 'direccion')
    inlines = [ViviendaInline]
    
    def total_viviendas(self, obj):
        return obj.viviendas.count()
    total_viviendas.short_description = 'Total de viviendas'

class ResidenteInline(admin.TabularInline):
    model = Residente
    extra = 0

class ViviendaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'piso', 'edificio', 'metros_cuadrados', 'habitaciones', 'baños', 'estado', 'total_residentes')
    list_filter = ('edificio', 'estado', 'piso')
    search_fields = ('numero', 'edificio__nombre')
    inlines = [ResidenteInline]
    
    def total_residentes(self, obj):
        return obj.residentes.count()
    total_residentes.short_description = 'Total de residentes'

class ResidenteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'vivienda', 'es_propietario', 'fecha_ingreso', 'vehiculos')
    list_filter = ('es_propietario', 'vivienda__edificio')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'vivienda__numero')
    date_hierarchy = 'fecha_ingreso'

admin.site.register(Edificio, EdificioAdmin)
admin.site.register(Vivienda, ViviendaAdmin)
admin.site.register(Residente, ResidenteAdmin)
