document.addEventListener('DOMContentLoaded', function() {
    // Activar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Mostrar campo de placa solo cuando se selecciona vehículo
    const vehiculoCheckbox = document.getElementById('id_vehiculo');
    const placaField = document.getElementById('div_id_placa_vehiculo');
    
    if (vehiculoCheckbox && placaField) {
        function togglePlacaField() {
            if (vehiculoCheckbox.checked) {
                placaField.style.display = 'block';
            } else {
                placaField.style.display = 'none';
            }
        }
        
        // Ejecutar al cargar la página
        togglePlacaField();
        
        // Ejecutar cuando cambia el checkbox
        vehiculoCheckbox.addEventListener('change', togglePlacaField);
    }
    
    // Filtrar residentes según la vivienda seleccionada
    const viviendaSelect = document.getElementById('id_vivienda_destino');
    const residenteSelect = document.getElementById('id_residente_autoriza');
    
    if (viviendaSelect && residenteSelect) {
        viviendaSelect.addEventListener('change', function() {
            const viviendaId = this.value;
            
            // Desactivar el select de residentes mientras se carga
            residenteSelect.disabled = true;
            
            // Fetch para obtener los residentes de la vivienda seleccionada
            fetch(`/api/viviendas/${viviendaId}/residentes/`)
                .then(response => response.json())
                .then(data => {
                    // Limpiar opciones actuales
                    residenteSelect.innerHTML = '';
                    
                    // Agregar nueva opción vacía
                    let emptyOption = document.createElement('option');
                    emptyOption.value = '';
                    emptyOption.textContent = '---------';
                    residenteSelect.appendChild(emptyOption);
                    
                    // Agregar opciones de residentes (solo activos)
                    data.forEach(residente => {
                        // Verificar si el residente está activo
                        if (residente.activo) {
                            let option = document.createElement('option');
                            option.value = residente.id;
                            option.textContent = residente.nombre;
                            residenteSelect.appendChild(option);
                        }
                    });
                    
                    // Reactivar el select
                    residenteSelect.disabled = false;
                })
                .catch(error => {
                    console.error('Error al cargar residentes:', error);
                    residenteSelect.disabled = false;
                });
        });
    }
    
    // Función para configurar los switch de mostrar/ocultar inactivos
    function setupInactivosSwitch(switchId, elementClass) {
        const checkbox = document.getElementById(switchId);
        if (checkbox) {
            const elementosInactivos = document.querySelectorAll('.' + elementClass);
            
            checkbox.addEventListener('change', function() {
                elementosInactivos.forEach(function(elemento) {
                    if (checkbox.checked) {
                        elemento.classList.remove('d-none');
                    } else {
                        elemento.classList.add('d-none');
                    }
                });
            });
        }
    }
    
    // Configurar los switches
    setupInactivosSwitch('mostrarInactivos', 'usuario-inactivo');
    setupInactivosSwitch('mostrarInactivosVivienda', 'residente-inactivo-vivienda');
    setupInactivosSwitch('mostrarInactivos', 'residente-inactivo');
    
    // Hacer que los mensajes de alerta se cierren automáticamente después de 5 segundos
    const alertList = document.querySelectorAll('.alert');
    alertList.forEach(function(alert) {
        setTimeout(function() {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
});