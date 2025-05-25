from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Visita, MovimientoResidente
from viviendas.models import Residente, Vivienda
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import qrcode
import io
import base64
from django.views.decorators.http import require_GET, require_POST
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from accesos.qr_firma_utils import generar_firma_qr, verificar_firma_qr
import json

@login_required
def historial_visitas(request):
    """API endpoint para obtener el historial de visitas completadas (con salida registrada)"""
    visitas = Visita.objects.filter(fecha_hora_salida__isnull=False).order_by('-fecha_hora_salida')[:100]  # Limitar a las 100 más recientes
    
    data = []
    for visita in visitas:
        data.append({
            'id': visita.id,
            'nombre_visitante': visita.nombre_visitante,
            'documento_visitante': visita.documento_visitante,
            'vivienda_destino': str(visita.vivienda_destino),
            'residente_autoriza': str(visita.residente_autoriza),
            'fecha_hora_entrada': visita.fecha_hora_entrada.isoformat(),
            'fecha_hora_salida': visita.fecha_hora_salida.isoformat() if visita.fecha_hora_salida else None,
            'motivo': visita.motivo,
            'registrado_por': str(visita.registrado_por) if visita.registrado_por else None
        })
    
    return JsonResponse(data, safe=False)

@login_required
def residentes_por_vivienda(request, vivienda_id):
    """API endpoint para obtener los residentes de una vivienda específica (solo activos)"""
    try:
        vivienda = Vivienda.objects.get(pk=vivienda_id)
        residentes = vivienda.residentes.filter(activo=True)
        
        data = []
        for residente in residentes:
            data.append({
                'id': residente.id,
                'nombre': f"{residente.usuario.first_name} {residente.usuario.last_name}",
                'tipo': residente.tipo_residente.nombre,
                'es_propietario': residente.tipo_residente.es_propietario,
                'activo': residente.activo
            })
        
        return JsonResponse(data, safe=False)
    except Vivienda.DoesNotExist:
        return JsonResponse({'error': 'Vivienda no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_GET
@login_required
def generar_qr_visita(request, visita_id):
    try:
        visita = Visita.objects.get(pk=visita_id, residente_autoriza__usuario=request.user)

        datos_qr = {
            "id": visita.id,
            "nombre_visitante": visita.nombre_visitante,
            "documento_visitante": visita.documento_visitante,
            "vivienda": str(visita.vivienda_destino),
            "autorizado_por": str(visita.residente_autoriza),
            "fecha": visita.fecha_hora_entrada.strftime("%Y-%m-%d %H:%M"),
            "firma": generar_firma_qr(visita.id)
        }

        qr = qrcode.make(datos_qr)
        buffer = io.BytesIO()
        qr.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return JsonResponse({"qr_base64": qr_base64})
    
    except Visita.DoesNotExist:
        return JsonResponse({"error": "Visita no encontrada o no autorizada para este usuario"}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verificar_qr_visita(request):
    data = request.data
    visita_id = data.get('id')
    firma = data.get('firma')

    if not visita_id or not firma:
        return Response({'valido': False, 'mensaje': 'ID y firma requeridos.'}, status=400)

    # Verificar la firma antes de continuar
    if not verificar_firma_qr(int(visita_id), firma):
        return Response({'valido': False, 'mensaje': 'QR inválido o alterado.'}, status=403)

    try:
        visita = Visita.objects.get(id=visita_id)

        if visita.fecha_hora_salida:
            return Response({'valido': False, 'mensaje': 'Esta visita ya fue finalizada.'})

        return Response({
            'valido': True,
            'mensaje': 'QR verificado correctamente.',
            'visitante': visita.nombre_visitante,
            'documento': visita.documento_visitante,
            'vivienda': str(visita.vivienda_destino),
            'fecha': visita.fecha_hora_entrada.strftime('%Y-%m-%d %H:%M'),
            'motivo': visita.motivo,
            'autorizado_por': str(visita.residente_autoriza)
        })

    except Visita.DoesNotExist:
        return Response({'valido': False, 'mensaje': 'No se encontró una visita válida con ese ID.'}, status=404)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_visita(request):
    try:
        data = request.data
        nombre = data.get('nombre_visitante')
        documento = data.get('documento_visitante')
        vivienda_id = data.get('vivienda_destino_id')
        motivo = data.get('motivo', '')

        if not all([nombre, documento, vivienda_id]):
            return Response({'error': 'Faltan datos obligatorios'}, status=status.HTTP_400_BAD_REQUEST)

        vivienda = Vivienda.objects.get(pk=vivienda_id)
        residente = Residente.objects.get(usuario=request.user)

        visita = Visita.objects.create(
            nombre_visitante=nombre,
            documento_visitante=documento,
            vivienda_destino=vivienda,
            residente_autoriza=residente,
            motivo=motivo,
            registrado_por=request.user,
            fecha_hora_entrada=timezone.now()
        )
        # 📦 Generar el QR
        datos_qr = {
            "id": visita.id,
            # "nombre_visitante": visita.nombre_visitante,
            # "documento_visitante": visita.documento_visitante,
            # "vivienda": str(visita.vivienda_destino),
            # "autorizado_por": str(visita.residente_autoriza),
            # "fecha": visita.fecha_hora_entrada.strftime("%Y-%m-%d %H:%M"),
            "firma": generar_firma_qr(visita.id)
        }
        qr = qrcode.make(json.dumps(datos_qr))
        buffer = io.BytesIO()
        qr.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return Response({
            'mensaje': 'Visita registrada correctamente',
            'id': visita.id,
            'qr_base64': qr_base64
        })

    except Vivienda.DoesNotExist:
        return Response({'error': 'Vivienda no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except Residente.DoesNotExist:
        return Response({'error': 'Residente no autorizado'}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

