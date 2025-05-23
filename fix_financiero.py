#!/usr/bin/env python
"""
Script para corregir automáticamente las agregaciones problemáticas
"""

import re

def fix_views_file():
    """Corrige el archivo de vistas"""
    
    # Leer el archivo
    with open('financiero/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patterns a corregir
    patterns = [
        # Sum simple sin output_field
        (r'Sum\(\'(\w+)\'\)', r"Sum('\1', output_field=DecimalField())"),
        
        # Coalesce con Sum
        (r'Coalesce\(Sum\(\'(\w+)\'\), (\d+)\)', 
         r"Coalesce(Sum('\1', output_field=DecimalField()), Decimal('\2'))"),
        
        # Coalesce con Sum y Decimal
        (r'Coalesce\(Sum\(\'(\w+)\'\), Decimal\(\'(\d+)\'\)\)', 
         r"Coalesce(Sum('\1', output_field=DecimalField()), Decimal('\2'))"),
    ]
    
    # Aplicar correcciones
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Asegurar imports
    if 'from django.db.models import' in content:
        content = content.replace(
            'from django.db.models import Sum, Count, Q, F, ExpressionWrapper, DecimalField',
            'from django.db.models import Sum, Count, Q, F, ExpressionWrapper, DecimalField'
        )
    
    # Escribir archivo corregido
    with open('financiero/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Archivo financiero/views.py corregido")

if __name__ == "__main__":
    fix_views_file()