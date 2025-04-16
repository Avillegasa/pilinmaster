from rest_framework import serializers
from .models import Usuario, Rol
# Esto nos permite serializar al usuario para respuestas personalizadas despues del login
class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion']
class UsuarioSerializer(serializers.ModelSerializer):
    rol = RolSerializer(read_only=True)
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'rol', 'telefono', 'tipo_documento', 'numero_documento', 'foto']
