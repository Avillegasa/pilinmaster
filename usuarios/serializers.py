from rest_framework import serializers 
from .models import Usuario, Rol
from viviendas.models import Residente

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion']

class UsuarioSerializer(serializers.ModelSerializer):
    rol = RolSerializer(read_only=True)
    vivienda_id = serializers.SerializerMethodField() 

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'rol', 'telefono', 'tipo_documento', 'numero_documento',
            'foto', 'vivienda_id' 
        ]

    def get_vivienda_id(self, obj):
        try:
            return obj.residente.vivienda.id if obj.residente and obj.residente.vivienda else None
        except Exception:
            return None
