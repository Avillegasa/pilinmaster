from django.contrib import admin
from .models import Alerta

@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'descripcion', 'enviado_por', 'fecha')
    list_filter = ('tipo', 'fecha')
