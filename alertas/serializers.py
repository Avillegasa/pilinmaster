from rest_framework import serializers
from .models import Alerta  # Asegúrate que tienes un modelo llamado Alerta

class AlertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alerta
        fields = '__all__'
