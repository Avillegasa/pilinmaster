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
                // Limpiar el campo cuando se desmarca
                const placaInput = placaField.querySelector('input');
                if (placaInput) {
                    placaInput.value = '';
                }
            }
        }
        
        // Ejecutar al cargar la página
        togglePlacaField();
        
        // Ejecutar cuando cambia el checkbox
        vehiculoCheckbox.addEventListener('change', togglePlacaField);
    }
    
    // Filtrar residentes según la vivienda seleccionada - con mejoras de usabilidad móvil
    const viviendaSelect = document.getElementById('id_vivienda_destino');
    const residenteSelect = document.getElementById('id_residente_autoriza');
    
    if (viviendaSelect && residenteSelect) {
        viviendaSelect.addEventListener('change', function() {
            const viviendaId = this.value;
            
            // Mostrar indicador de carga
            residenteSelect.disabled = true;
            const originalHTML = residenteSelect.innerHTML;
            residenteSelect.innerHTML = '<option value="">Cargando residentes...</option>';
            
            // Actualizar opción seleccionada en móviles (UX mejorada)
            viviendaSelect.blur();
            
            // Fetch para obtener los residentes de la vivienda seleccionada
            fetch(`/api/viviendas/${viviendaId}/residentes/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Error: ${response.status}`);
                    }
                    return response.json();
                })
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
                    
                    // Si no hay residentes, mostrar un mensaje
                    if (data.length === 0 || !data.some(r => r.activo)) {
                        let noResidentesOption = document.createElement('option');
                        noResidentesOption.value = '';
                        noResidentesOption.textContent = 'No hay residentes activos';
                        noResidentesOption.disabled = true;
                        residenteSelect.appendChild(noResidentesOption);
                    }
                })
                .catch(error => {
                    console.error('Error al cargar residentes:', error);
                    residenteSelect.innerHTML = originalHTML;
                    residenteSelect.disabled = false;
                    
                    // Mostrar un mensaje de error
                    alert('Error al cargar residentes. Por favor, inténtelo de nuevo.');
                });
        });
    }
    
    // Función para configurar los switch de mostrar/ocultar inactivos - con mejora de experiencia táctil
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
                
                // Actualizar etiqueta para mejor UX
                const label = checkbox.closest('.form-check').querySelector('.form-check-label');
                if (label) {
                    if (checkbox.checked) {
                        label.innerHTML = 'Ocultar inactivos';
                    } else {
                        label.innerHTML = 'Mostrar inactivos';
                    }
                }
            });
            
            // Inicializar la etiqueta
            const label = checkbox.closest('.form-check').querySelector('.form-check-label');
            if (label && !label.dataset.originalText) {
                label.dataset.originalText = label.innerHTML;
            }
        }
    }
    
    // Configurar los switches
    setupInactivosSwitch('mostrarInactivos', 'usuario-inactivo');
    setupInactivosSwitch('mostrarInactivosVivienda', 'residente-inactivo-vivienda');
    setupInactivosSwitch('mostrarInactivos', 'residente-inactivo');
    setupInactivosSwitch('mostrarInactivosEmpleado', 'empleado-inactivo');
    
    // Hacer que los mensajes de alerta se cierren automáticamente después de 5 segundos
    const alertList = document.querySelectorAll('.alert:not(.alert-important)');
    alertList.forEach(function(alert) {
        setTimeout(function() {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
    
    // Optimizar navegación móvil - Colapsar sidebar al hacer clic en un enlace
    if (window.innerWidth < 768) {
        const sidebarLinks = document.querySelectorAll('#sidebarMenu .nav-link');
        const sidebarMenu = document.getElementById('sidebarMenu');
        const sidebarCollapse = new bootstrap.Collapse(sidebarMenu, {toggle: false});
        
        sidebarLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                if (window.innerWidth < 768 && sidebarMenu.classList.contains('show')) {
                    sidebarCollapse.hide();
                }
            });
        });
    }
    
    // Gestionar secciones colapsables en el sidebar para móviles
    const headings = document.querySelectorAll('.sidebar-heading');
    headings.forEach(heading => {
        const toggleIcon = heading.querySelector('[data-bs-toggle]');
        if (toggleIcon) {
            toggleIcon.addEventListener('click', function() {
                const target = document.getElementById(this.dataset.bsTarget.substring(1));
                const expanded = this.getAttribute('aria-expanded') === 'true' || false;
                
                // Rotar icono
                this.querySelector('i').style.transform = expanded ? 'rotate(0deg)' : 'rotate(180deg)';
            });
        }
    });
    
    // Mejora para formularios de filtro con autosubmit en móviles
    const autoSubmitSelects = document.querySelectorAll('select[data-autosubmit="true"]');
    autoSubmitSelects.forEach(select => {
        // En dispositivos móviles, desactivar el autosubmit para mejor UX
        if (window.innerWidth < 768) {
            select.setAttribute('data-autosubmit', 'false');
        }
    });
    
    // Agregar botón para volver arriba en páginas largas (útil en móviles)
    const body = document.querySelector('body');
    const backToTopButton = document.createElement('button');
    backToTopButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTopButton.className = 'back-to-top btn btn-primary rounded-circle';
    backToTopButton.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 99; display: none; width: 40px; height: 40px; border-radius: 50%; opacity: 0.7;';
    body.appendChild(backToTopButton);
    
    // Mostrar/ocultar botón según el scroll
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    });
    
    // Funcionalidad del botón volver arriba
    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // Mejora para tablas responsivas (convertir a cards en móviles)
    const tables = document.querySelectorAll('.table-responsive-card');
    if (window.innerWidth <= 576 && tables.length > 0) {
        tables.forEach(table => {
            const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                cells.forEach((cell, index) => {
                    if (headers[index] && !cell.hasAttribute('data-label')) {
                        cell.setAttribute('data-label', headers[index]);
                    }
                });
            });
        });
    }
    
    // Optimización para formularios con muchos campos en móviles
    if (window.innerWidth < 768) {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            // Añadir clase para reducir espaciado en móviles
            form.classList.add('form-mobile-compact');
            
            // Hacer que los botones de submit tengan ancho completo en móviles
            const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"]');
            submitButtons.forEach(button => {
                button.classList.add('w-100', 'mb-2');
            });
        });
    }
});