from rest_framework import serializers
from .models import Usuario
# Esto nos permite serializar al usuario para respuestas personalizadas despues del login
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'rol', 'telefono', 'tipo_documento', 'numero_documento', 'foto']
