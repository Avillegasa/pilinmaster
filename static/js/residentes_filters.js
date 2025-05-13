document.addEventListener('DOMContentLoaded', function() {
    // Elementos DOM
    const edificioSelect = document.getElementById('edificio');
    const viviendaSelect = document.getElementById('vivienda');
    const tipoSelect = document.getElementById('es_propietario');
    const estadoSelect = document.getElementById('estado');
    const filtroForm = document.getElementById('filtroForm');
    
    // Función para actualizar las viviendas según el edificio seleccionado
    function actualizarViviendas() {
        if (!edificioSelect || !viviendaSelect) return;
        
        const edificioId = edificioSelect.value;
        
        // Limpiar viviendas actuales
        viviendaSelect.innerHTML = '<option value="">Todas las viviendas</option>';
        
        if (!edificioId) {
            viviendaSelect.disabled = true;
            return;
        }
        
        // Habilitar el select de vivienda
        viviendaSelect.disabled = false;
        
        // Mostrar indicador de carga
        viviendaSelect.innerHTML = '<option value="">Cargando viviendas...</option>';
        
        // Hacer la petición para obtener las viviendas del edificio seleccionado
        fetch(`/viviendas/api/edificio/${edificioId}/viviendas/`)
            .then(response => response.json())
            .then(data => {
                // Limpiar las opciones actuales
                viviendaSelect.innerHTML = '<option value="">Todas las viviendas</option>';
                
                // Añadir las nuevas viviendas
                data.forEach(vivienda => {
                    const option = document.createElement('option');
                    option.value = vivienda.id;
                    option.textContent = `${vivienda.numero} (Piso ${vivienda.piso})`;
                    viviendaSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error al cargar viviendas:', error);
                viviendaSelect.innerHTML = '<option value="">Error al cargar viviendas</option>';
            });
    }
    
    // Añadir event listeners
    if (edificioSelect) {
        edificioSelect.addEventListener('change', function() {
            actualizarViviendas();
            // No enviamos el formulario automáticamente para permitir seleccionar la vivienda
        });
    }
    
    if (viviendaSelect) {
        viviendaSelect.addEventListener('change', function() {
            filtroForm.submit();
        });
    }
    
    if (tipoSelect) {
        tipoSelect.addEventListener('change', function() {
            filtroForm.submit();
        });
    }
    
    if (estadoSelect) {
        estadoSelect.addEventListener('change', function() {
            filtroForm.submit();
        });
    }
    
    // Inicializar viviendas si hay un edificio seleccionado
    if (edificioSelect && edificioSelect.value) {
        actualizarViviendas();
    }
});