from rest_framework import viewsets
from .models import Alerta
from .serializers import AlertaSerializer

class AlertaViewSet(viewsets.ModelViewSet):
    queryset = Alerta.objects.all().order_by('-fecha_creacion')
    serializer_class = AlertaSerializer
