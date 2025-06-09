from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .models import Alerta
from .serializers import AlertaSerializer, CrearAlertaSerializer

class AlertaCreateView(CreateAPIView):
    queryset = Alerta.objects.all()
    serializer_class = CrearAlertaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(enviado_por=self.request.user)

class AlertaViewSet(ModelViewSet):
    queryset = Alerta.objects.all()
    serializer_class = AlertaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Alerta.objects.all()
        # Filtrar por usuario si se especifica
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            queryset = queryset.filter(enviado_por__id=user_id)
        return queryset.order_by('-fecha')
    
    def perform_create(self, serializer):
        # Asignar automáticamente el usuario que envía la alerta
        serializer.save(enviado_por=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def crear_alerta(request):
    """
    Crear una nueva alerta
    """
    serializer = CrearAlertaSerializer(data=request.data)
    if serializer.is_valid():
        alerta = serializer.save(enviado_por=request.user)
        
        # Retornar la alerta completa con información del usuario
        response_serializer = AlertaSerializer(alerta)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mis_alertas(request):
    """
    Obtener todas las alertas del usuario autenticado
    """
    alertas = Alerta.objects.filter(enviado_por=request.user).order_by('-fecha')
    serializer = AlertaSerializer(alertas, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def actualizar_estado_alerta(request, pk):
    """
    Actualizar el estado de una alerta (solo para staff)
    """
    try:
        alerta = Alerta.objects.get(pk=pk)
        
        # Solo el staff puede cambiar el estado
        if not request.user.is_staff:
            return Response(
                {'error': 'No tienes permisos para actualizar alertas'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        nuevo_estado = request.data.get('estado')
        if nuevo_estado in ['pendiente', 'en_proceso', 'resuelto']:
            alerta.estado = nuevo_estado
            if nuevo_estado in ['en_proceso', 'resuelto']:
                alerta.atendido_por = request.user
                alerta.fecha_atencion = timezone.now()
            alerta.save()
            
            serializer = AlertaSerializer(alerta)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Estado inválido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Alerta.DoesNotExist:
        return Response(
            {'error': 'Alerta no encontrada'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@login_required
def lista_alertas(request):
    """
    Vista HTML para mostrar la lista de alertas en el dashboard
    """
    alertas = Alerta.objects.all().order_by('-fecha')
    
    # Filtrar por usuario si se especifica
    user_id = request.GET.get('user_id')
    if user_id:
        alertas = alertas.filter(enviado_por__id=user_id)
    
    # Calcular estadísticas
    alertas_pendientes = alertas.filter(estado='pendiente').count()
    alertas_proceso = alertas.filter(estado='en_proceso').count()
    alertas_resueltas = alertas.filter(estado='resuelto').count()
    
    context = {
        'alertas': alertas,
        'user': request.user,
        'alertas_pendientes': alertas_pendientes,
        'alertas_proceso': alertas_proceso,
        'alertas_resueltas': alertas_resueltas,
    }
    
    return render(request, 'alertas/lista_alertas.html', context)

@login_required
@require_http_methods(["PUT"])
def cambiar_estado_web(request, pk):
    """
    Cambiar estado de alerta desde la web (usa autenticación de Django)
    """
    try:
        # Solo staff puede cambiar estados
        if not request.user.is_staff:
            return JsonResponse(
                {'error': 'No tienes permisos para actualizar alertas'}, 
                status=403
            )
        
        # Obtener la alerta
        alerta = Alerta.objects.get(pk=pk)
        
        # Parsear el JSON del body
        data = json.loads(request.body)
        nuevo_estado = data.get('estado')
        
        # Validar estado
        if nuevo_estado not in ['pendiente', 'en_proceso', 'resuelto']:
            return JsonResponse(
                {'error': 'Estado inválido'}, 
                status=400
            )
        
        # Actualizar alerta
        alerta.estado = nuevo_estado
        if nuevo_estado in ['en_proceso', 'resuelto']:
            alerta.atendido_por = request.user
            alerta.fecha_atencion = timezone.now()
        alerta.save()
        
        # Preparar respuesta
        response_data = {
            'id': alerta.id,
            'estado': alerta.estado,
            'atendido_por_info': None
        }
        
        if alerta.atendido_por:
            response_data['atendido_por_info'] = {
                'username': alerta.atendido_por.username,
                'first_name': alerta.atendido_por.first_name,
                'last_name': alerta.atendido_por.last_name,
            }
        
        return JsonResponse(response_data)
        
    except Alerta.DoesNotExist:
        return JsonResponse(
            {'error': 'Alerta no encontrada'}, 
            status=404
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {'error': 'Datos JSON inválidos'}, 
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {'error': f'Error interno: {str(e)}'}, 
            status=500
        )