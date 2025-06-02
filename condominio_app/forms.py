# condominio_app/forms.py
"""
Este archivo reexporta formularios de las aplicaciones específicas
para mantener compatibilidad con el código existente.
"""

# Importar formularios específicos que puedan ser necesarios
from usuarios.forms import UsuarioCreationForm, UsuarioChangeForm, RolForm
from viviendas.forms import EdificioForm, ViviendaForm, ResidenteForm
from accesos.forms import VisitaForm, MovimientoResidenteEntradaForm, MovimientoResidenteSalidaForm

# No es necesario definir nuevos formularios aquí