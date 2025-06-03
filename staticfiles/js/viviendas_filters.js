document.addEventListener('DOMContentLoaded', function() {
    // Elementos DOM
    const edificioSelect = document.getElementById('edificio');
    const pisoSelect = document.getElementById('piso');
    const estadoSelect = document.getElementById('estado');
    const activoSelect = document.getElementById('activo');
    const filtroForm = document.getElementById('filtroForm');
    
    // Función para actualizar los pisos disponibles según el edificio seleccionado
    function actualizarPisos() {
        if (!edificioSelect || !pisoSelect) return;
        
        const edificioId = edificioSelect.value || 0;
        
        // Guardar el piso seleccionado actualmente
        const pisoSeleccionado = pisoSelect.value;
        
        // Deshabilitar temporalmente el select de pisos
        pisoSelect.disabled = true;
        
        // Hacer la petición para obtener los pisos del edificio seleccionado
        fetch(`/viviendas/api/edificio/${edificioId}/pisos/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error de red: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                // Limpiar las opciones actuales
                pisoSelect.innerHTML = '<option value="">Todos los pisos</option>';
                
                // Añadir los nuevos pisos
                data.forEach(piso => {
                    const option = document.createElement('option');
                    option.value = piso;
                    option.textContent = `Piso ${piso}`;
                    pisoSelect.appendChild(option);
                });
                
                // Intentar restaurar el piso seleccionado previamente
                if (pisoSeleccionado) {
                    pisoSelect.value = pisoSeleccionado;
                }
                
                // Habilitar el select de pisos
                pisoSelect.disabled = false;
            })
            .catch(error => {
                console.error('Error al cargar pisos:', error);
                pisoSelect.disabled = false;
            });
    }
    
    // Función para manejar la relación entre estado y activo
    function sincronizarEstadoActivo() {
        if (!estadoSelect || !activoSelect) return;
        
        // Si se selecciona BAJA, automáticamente cambiar activo a false
        if (estadoSelect.value === 'BAJA') {
            activoSelect.value = 'false';
        }
        
        // Si se selecciona inactivo, solo permitir BAJA como estado
        if (activoSelect.value === 'false') {
            if (estadoSelect.value !== 'BAJA') {
                estadoSelect.value = 'BAJA';
            }
        }
    }
    
    // Añadir event listeners
    if (edificioSelect) {
        edificioSelect.addEventListener('change', function() {
            actualizarPisos();
            // Solo enviamos el formulario si el usuario ha terminado de seleccionar
            // Esto permite tiempo para seleccionar también el piso
            if (this.dataset.autosubmit === "true") {
                filtroForm.submit();
            }
        });
    }
    
    if (pisoSelect) {
        pisoSelect.addEventListener('change', function() {
            filtroForm.submit();
        });
    }
    
    if (estadoSelect) {
        estadoSelect.addEventListener('change', function() {
            sincronizarEstadoActivo();
            filtroForm.submit();
        });
    }
    
    if (activoSelect) {
        activoSelect.addEventListener('change', function() {
            sincronizarEstadoActivo();
            filtroForm.submit();
        });
    }
    
    // Inicializar
    sincronizarEstadoActivo();
    
    // Cargar pisos si hay un edificio seleccionado
    if (edificioSelect && edificioSelect.value) {
        actualizarPisos();
    }
});