document.addEventListener('DOMContentLoaded', function() {
    // Elementos DOM
    const edificioSelect = document.getElementById('id_edificio');
    const viviendaSelect = document.getElementById('id_vivienda');
    const empleadoSelect = document.getElementById('id_empleado');
    const tipoSelect = document.getElementById('id_tipo');
    const estadoSelect = document.getElementById('id_estado');
    const fechaDesdeInput = document.getElementById('id_fecha_desde');
    const fechaHastaInput = document.getElementById('id_fecha_hasta');
    const filtroForm = document.getElementById('filtroForm');
    
    // Función para actualizar las viviendas según el edificio seleccionado
    function actualizarViviendas() {
        if (!edificioSelect || !viviendaSelect) return;
        
        const edificioId = edificioSelect.value;
        
        // Limpiar viviendas actuales
        viviendaSelect.innerHTML = '<option value="">Todas las viviendas</option>';
        
        if (!edificioId) {
            return;
        }
        
        // Mostrar indicador de carga
        viviendaSelect.innerHTML = '<option value="">Cargando viviendas...</option>';
        
        // Hacer la petición para obtener las viviendas del edificio seleccionado
        fetch(`/personal/api/edificio/${edificioId}/viviendas/`)
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
    
    // Validación de fechas
    function validarFechas() {
        if (!fechaDesdeInput || !fechaHastaInput) return true;
        
        const fechaDesde = fechaDesdeInput.value ? new Date(fechaDesdeInput.value) : null;
        const fechaHasta = fechaHastaInput.value ? new Date(fechaHastaInput.value) : null;
        
        if (fechaDesde && fechaHasta && fechaDesde > fechaHasta) {
            alert('La fecha desde no puede ser posterior a la fecha hasta');
            return false;
        }
        
        return true;
    }
    
    // Añadir event listeners
    if (edificioSelect) {
        edificioSelect.addEventListener('change', function() {
            actualizarViviendas();
        });
    }
    
    // Añadir event listener al formulario para validar antes de enviar
    if (filtroForm) {
        filtroForm.addEventListener('submit', function(e) {
            if (!validarFechas()) {
                e.preventDefault();
            }
        });
    }
    
    // Inicializar viviendas si hay un edificio seleccionado
    if (edificioSelect && edificioSelect.value) {
        actualizarViviendas();
    }
});