from django import template

register = template.Library()

@register.filter
def unique_items(queryset, field_name):
    """
    Devuelve una lista de valores únicos para un campo específico 
    en un queryset o lista de objetos.
    
    Uso: {{ queryset|unique_items:'field_name' }}
    
    Ejemplos:
    - {{ edificio.viviendas.all|unique_items:'piso' }} -> Devuelve una lista de pisos únicos
    - {{ residentes|unique_items:'tipo_residente.nombre' }} -> Devuelve una lista de nombres de tipo de residente
    
    Acepta:
    - QuerySets
    - Listas de objetos modelo
    - Listas de diccionarios
    
    Puede acceder a campos anidados usando la notación de punto, por ejemplo: 'relacionado.campo'
    """
    if not queryset:
        return []
    
    # Si tenemos un acceso a campo anidado (por ejemplo 'tipo_residente.nombre')
    if '.' in field_name:
        parts = field_name.split('.')
        values = []
        
        for item in queryset:
            # Navegar a través de los campos anidados
            value = item
            for part in parts:
                if hasattr(value, part):
                    value = getattr(value, part)
                elif isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    value = None
                    break
            
            if value is not None:
                values.append(value)
        
    # Si es un acceso simple a un campo
    else:
        # Si es un queryset o lista de objetos
        if hasattr(queryset[0], field_name):
            values = [getattr(item, field_name) for item in queryset]
        # Si es una lista de diccionarios
        elif isinstance(queryset[0], dict) and field_name in queryset[0]:
            values = [item[field_name] for item in queryset]
        else:
            return []
    
    # Devolver valores únicos ordenados (ignorar None)
    return sorted(set(v for v in values if v is not None))