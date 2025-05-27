from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def duration_until(start_time, end_time):
    """
    Calcula la duración entre dos fechas y la devuelve en formato legible
    """
    if not start_time or not end_time:
        return "N/A"
    
    try:
        duration = end_time - start_time
        
        # Obtener días, horas y minutos
        days = duration.days
        seconds = duration.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        # Formatear la duración
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        
        if not parts:
            return "< 1m"
        
        return " ".join(parts)
    except:
        return "N/A"

@register.filter
def time_since_now(datetime_obj):
    """
    Calcula el tiempo transcurrido desde una fecha hasta ahora
    """
    if not datetime_obj:
        return "N/A"
    
    try:
        now = timezone.now()
        duration = now - datetime_obj
        
        days = duration.days
        seconds = duration.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if days > 0:
            return f"hace {days} día{'s' if days != 1 else ''}"
        elif hours > 0:
            return f"hace {hours} hora{'s' if hours != 1 else ''}"
        elif minutes > 0:
            return f"hace {minutes} minuto{'s' if minutes != 1 else ''}"
        else:
            return "hace un momento"
    except:
        return "N/A"

@register.filter
def badge_for_status(status):
    """
    Devuelve la clase CSS apropiada para un estado
    """
    status_classes = {
        'ACTIVA': 'badge-success',
        'FINALIZADA': 'badge-secondary',
        'ENTRADA': 'badge-success',
        'SALIDA': 'badge-danger',
        'PENDIENTE': 'badge-warning',
        'COMPLETADO': 'badge-success',
        'CANCELADO': 'badge-danger',
    }
    return status_classes.get(status.upper(), 'badge-secondary')