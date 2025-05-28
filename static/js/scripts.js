document.addEventListener('DOMContentLoaded', function() {
    // Activar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // ✅ NUEVA FUNCIONALIDAD: Protección de usuarios administradores
    const proteccionUsuarios = {
        init: function() {
            this.protegerBotonesAdmin();
            this.validarFormularios();
            this.configurarConfirmaciones();
        },
        
        protegerBotonesAdmin: function() {
            // Proteger botones de cambio de estado para administradores
            const botonesEstado = document.querySelectorAll('a[href*="usuario-change-state"]');
            botonesEstado.forEach(boton => {
                boton.addEventListener('click', function(e) {
                    const fila = this.closest('tr');
                    const iconoCrown = fila.querySelector('.fa-crown');
                    
                    if (iconoCrown) {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        // Usar SweetAlert2 si está disponible, sino usar alert nativo
                        if (typeof Swal !== 'undefined') {
                            Swal.fire({
                                icon: 'error',
                                title: '❌ Operación Denegada',
                                text: 'Los usuarios Administradores están protegidos por razones de seguridad.',
                                confirmButtonText: 'Entendido',
                                confirmButtonColor: '#dc3545'
                            });
                        } else {
                            alert('❌ OPERACIÓN DENEGADA: Los usuarios Administradores están protegidos por razones de seguridad.');
                        }
                        
                        return false;
                    }
                });
            });
            
            // Proteger botones de eliminación de roles
            const botonesEliminarRol = document.querySelectorAll('a[href*="rol"][href*="delete"]');
            botonesEliminarRol.forEach(boton => {
                boton.addEventListener('click', function(e) {
                    const fila = this.closest('tr');
                    const nombreRol = fila.querySelector('td:nth-child(2)').textContent.trim();
                    
                    if (nombreRol === 'Administrador') {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        if (typeof Swal !== 'undefined') {
                            Swal.fire({
                                icon: 'error',
                                title: '❌ Operación Denegada',
                                text: 'El rol "Administrador" no puede ser eliminado por razones de seguridad del sistema.',
                                confirmButtonText: 'Entendido',
                                confirmButtonColor: '#dc3545'
                            });
                        } else {
                            alert('❌ OPERACIÓN DENEGADA: El rol "Administrador" no puede ser eliminado por razones de seguridad del sistema.');
                        }
                        
                        return false;
                    }
                });
            });
        },
        
        validarFormularios: function() {
            // Validar formulario de usuario antes del envío
            const formUsuario = document.querySelector('form[action*="usuario"]');
            if (formUsuario) {
                formUsuario.addEventListener('submit', function(e) {
                    const numeroDocumento = document.getElementById('id_numero_documento');
                    
                    if (numeroDocumento && numeroDocumento.value) {
                        // Validar que solo contenga números
                        const soloNumeros = /^\d+$/.test(numeroDocumento.value);
                        if (!soloNumeros) {
                            e.preventDefault();
                            
                            if (typeof Swal !== 'undefined') {
                                Swal.fire({
                                    icon: 'warning',
                                    title: 'Número de Documento Inválido',
                                    text: 'El número de cédula debe contener solo números.',
                                    confirmButtonText: 'Corregir',
                                    confirmButtonColor: '#ffc107'
                                });
                            } else {
                                alert('Número de Documento Inválido: El número de cédula debe contener solo números.');
                            }
                            
                            numeroDocumento.focus();
                            return false;
                        }
                        
                        // Validar longitud mínima
                        if (numeroDocumento.value.length < 7) {
                            e.preventDefault();
                            
                            if (typeof Swal !== 'undefined') {
                                Swal.fire({
                                    icon: 'warning',
                                    title: 'Número de Documento Muy Corto',
                                    text: 'El número de cédula debe tener al menos 7 dígitos.',
                                    confirmButtonText: 'Corregir',
                                    confirmButtonColor: '#ffc107'
                                });
                            } else {
                                alert('Número de Documento Muy Corto: El número de cédula debe tener al menos 7 dígitos.');
                            }
                            
                            numeroDocumento.focus();
                            return false;
                        }
                    }
                });
            }
        },
        
        configurarConfirmaciones: function() {
            // Confirmación mejorada para cambios de estado
            window.confirmarCambioEstado = function(username, esActivo) {
                const accion = esActivo ? 'desactivar' : 'activar';
                const titulo = esActivo ? '⚠️ Desactivar Usuario' : '✅ Activar Usuario';
                const texto = esActivo 
                    ? `¿Deseas desactivar al usuario "${username}"?\n\nEl usuario no podrá acceder al sistema hasta que sea reactivado.`
                    : `¿Deseas activar al usuario "${username}"?\n\nEl usuario podrá acceder nuevamente al sistema.`;
                
                if (typeof Swal !== 'undefined') {
                    return new Promise((resolve) => {
                        Swal.fire({
                            icon: esActivo ? 'warning' : 'question',
                            title: titulo,
                            text: texto,
                            showCancelButton: true,
                            confirmButtonText: esActivo ? 'Sí, desactivar' : 'Sí, activar',
                            cancelButtonText: 'Cancelar',
                            confirmButtonColor: esActivo ? '#dc3545' : '#28a745',
                            cancelButtonColor: '#6c757d'
                        }).then((result) => {
                            resolve(result.isConfirmed);
                        });
                    });
                } else {
                    // Fallback para navegadores sin SweetAlert2
                    return confirm(texto);
                }
            };
        },
        
        // ✅ NUEVA FUNCIÓN: Verificar protecciones mediante API
        verificarUsuarioModificable: async function(usuarioId) {
            try {
                const response = await fetch(`/usuarios/api/verificar-modificable/${usuarioId}/`);
                const data = await response.json();
                
                if (!data.modificable) {
                    if (typeof Swal !== 'undefined') {
                        Swal.fire({
                            icon: 'error',
                            title: '❌ Usuario Protegido',
                            text: data.mensaje,
                            confirmButtonText: 'Entendido',
                            confirmButtonColor: '#dc3545'
                        });
                    } else {
                        alert('❌ Usuario Protegido: ' + data.mensaje);
                    }
                    return false;
                }
                return true;
            } catch (error) {
                console.error('Error verificando usuario:', error);
                return false;
            }
        }
    };
    
    // Inicializar protecciones
    proteccionUsuarios.init();
    
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
                    if (typeof Swal !== 'undefined') {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error al cargar residentes',
                            text: 'No se pudieron cargar los residentes. Por favor, inténtelo de nuevo.',
                            confirmButtonText: 'Entendido',
                            confirmButtonColor: '#dc3545'
                        });
                    } else {
                        alert('Error al cargar residentes. Por favor, inténtelo de nuevo.');
                    }
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
    
    // ✅ NUEVA FUNCIONALIDAD: Validación en tiempo real para teléfono
    const telefonoInput = document.getElementById('id_telefono');
    if (telefonoInput) {
        telefonoInput.addEventListener('input', function(e) {
            // Permitir solo números
            let value = e.target.value.replace(/\D/g, '');
            e.target.value = value;
            
            // Validación visual
            const feedback = e.target.parentNode.querySelector('.invalid-feedback') || 
                           e.target.parentNode.querySelector('.form-text');
            
            if (value.length > 0 && value.length < 7) {
                e.target.classList.add('is-invalid');
                if (feedback) {
                    feedback.textContent = 'Debe tener al menos 7 dígitos';
                    feedback.className = 'text-danger small';
                }
            } else if (value.length >= 7 && value.length <= 15) {
                e.target.classList.remove('is-invalid');
                e.target.classList.add('is-valid');
                if (feedback) {
                    feedback.textContent = '✓ Teléfono válido';
                    feedback.className = 'text-success small';
                }
            } else if (value.length > 15) {
                e.target.classList.add('is-invalid');
                if (feedback) {
                    feedback.textContent = 'Máximo 15 dígitos';
                    feedback.className = 'text-danger small';
                }
                // Truncar a 15 dígitos
                e.target.value = value.substring(0, 15);
            } else {
                e.target.classList.remove('is-invalid', 'is-valid');
                if (feedback) {
                    feedback.textContent = 'Solo números. Mínimo 7, máximo 15 caracteres.';
                    feedback.className = 'form-text text-muted';
                }
            }
        });
        
        // Validación adicional al pegar contenido
        telefonoInput.addEventListener('paste', function(e) {
            setTimeout(() => {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length > 15) {
                    value = value.substring(0, 15);
                }
                e.target.value = value;
                e.target.dispatchEvent(new Event('input'));
            }, 10);
        });
    }
    const numeroDocumentoInput = document.getElementById('id_numero_documento');
    if (numeroDocumentoInput) {
        numeroDocumentoInput.addEventListener('input', function(e) {
            // Permitir solo números
            let value = e.target.value.replace(/\D/g, '');
            e.target.value = value;
            
            // Validación visual
            const feedback = e.target.parentNode.querySelector('.invalid-feedback') || 
                           e.target.parentNode.querySelector('.form-text');
            
            if (value.length > 0 && value.length < 7) {
                e.target.classList.add('is-invalid');
                if (feedback) {
                    feedback.textContent = 'Debe tener al menos 7 dígitos';
                    feedback.className = 'text-danger small';
                }
            } else if (value.length >= 7) {
                e.target.classList.remove('is-invalid');
                e.target.classList.add('is-valid');
                if (feedback) {
                    feedback.textContent = '✓ Número válido';
                    feedback.className = 'text-success small';
                }
            } else {
                e.target.classList.remove('is-invalid', 'is-valid');
                if (feedback) {
                    feedback.textContent = 'Solo números. Mínimo 7 caracteres.';
                    feedback.className = 'form-text text-muted';
                }
            }
        });
        
        // Validación adicional al pegar contenido
        numeroDocumentoInput.addEventListener('paste', function(e) {
            setTimeout(() => {
                let value = e.target.value.replace(/\D/g, '');
                e.target.value = value;
                e.target.dispatchEvent(new Event('input'));
            }, 10);
        });
    }
    
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
        
        if (sidebarMenu) {
            const sidebarCollapse = new bootstrap.Collapse(sidebarMenu, {toggle: false});
            
            sidebarLinks.forEach(function(link) {
                link.addEventListener('click', function() {
                    if (window.innerWidth < 768 && sidebarMenu.classList.contains('show')) {
                        sidebarCollapse.hide();
                    }
                });
            });
        }
    }
    
    // Gestionar secciones colapsables en el sidebar para móviles
    const headings = document.querySelectorAll('.sidebar-heading');
    headings.forEach(heading => {
        const toggleIcon = heading.querySelector('[data-bs-toggle]');
        if (toggleIcon) {
            toggleIcon.addEventListener('click', function() {
                const targetId = this.dataset.bsTarget;
                if (targetId) {
                    const target = document.getElementById(targetId.substring(1));
                    if (target) {
                        const expanded = this.getAttribute('aria-expanded') === 'true' || false;
                        
                        // Rotar icono
                        const icon = this.querySelector('i');
                        if (icon) {
                            icon.style.transform = expanded ? 'rotate(0deg)' : 'rotate(180deg)';
                        }
                    }
                }
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
    if (body) {
        const backToTopButton = document.createElement('button');
        backToTopButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
        backToTopButton.className = 'back-to-top btn btn-primary rounded-circle';
        backToTopButton.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 99; display: none; width: 40px; height: 40px; border-radius: 50%; opacity: 0.7;';
        backToTopButton.setAttribute('aria-label', 'Volver arriba');
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
    }
    
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
    
    // ✅ PROTECCIÓN ADICIONAL: Interceptar intentos de manipulación del DOM
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                // Re-aplicar protecciones si se añaden nuevos elementos
                proteccionUsuarios.protegerBotonesAdmin();
            }
        });
    });
    
    // Observar cambios en la tabla de usuarios
    const tablaUsuarios = document.querySelector('table tbody');
    if (tablaUsuarios) {
        observer.observe(tablaUsuarios, {
            childList: true,
            subtree: true
        });
    }
    
    // ✅ NUEVA FUNCIONALIDAD: Manejo de filtros mejorado
    const filtrosForm = document.querySelector('form[method="GET"]');
    if (filtrosForm) {
        // Aplicar filtros solo al hacer clic en el botón
        const botonFiltros = filtrosForm.querySelector('button[type="submit"]');
        const inputs = filtrosForm.querySelectorAll('input, select');
        
        // Prevenir auto-submit en móviles
        inputs.forEach(input => {
            if (input.type !== 'submit') {
                input.addEventListener('change', function(e) {
                    // No auto-enviar en móviles
                    if (window.innerWidth < 768) {
                        e.preventDefault();
                    }
                });
            }
        });
        
        // Limpiar filtros
        const botonLimpiar = document.createElement('button');
        botonLimpiar.type = 'button';
        botonLimpiar.className = 'btn btn-outline-secondary ms-2';
        botonLimpiar.innerHTML = '<i class="fas fa-eraser me-1"></i>Limpiar';
        
        if (botonFiltros && botonFiltros.parentNode) {
            botonFiltros.parentNode.appendChild(botonLimpiar);
            
            botonLimpiar.addEventListener('click', function() {
                inputs.forEach(input => {
                    if (input.type !== 'submit') {
                        input.value = '';
                    }
                });
                // Enviar formulario limpio
                filtrosForm.submit();
            });
        }
    }
    
    // ✅ NUEVA FUNCIONALIDAD: Indicador de carga para acciones
    function mostrarIndicadorCarga(elemento, mensaje = 'Procesando...') {
        const spinner = document.createElement('div');
        spinner.className = 'spinner-border spinner-border-sm me-2';
        spinner.setAttribute('role', 'status');
        
        const textoOriginal = elemento.innerHTML;
        elemento.innerHTML = '';
        elemento.appendChild(spinner);
        elemento.insertAdjacentText('beforeend', mensaje);
        elemento.disabled = true;
        
        return function() {
            elemento.innerHTML = textoOriginal;
            elemento.disabled = false;
        };
    }
    
    // Aplicar indicador de carga a botones de acción
    const botonesAccion = document.querySelectorAll('a[href*="change-state"], form button[type="submit"]');
    botonesAccion.forEach(boton => {
        if (boton.tagName === 'A') {
            boton.addEventListener('click', function() {
                if (!this.classList.contains('disabled')) {
                    const detenerCarga = mostrarIndicadorCarga(this, 'Procesando...');
                    // Detener carga después de 5 segundos como fallback
                    setTimeout(detenerCarga, 5000);
                }
            });
        }
    });
});

// ✅ FUNCIÓN GLOBAL: Verificar permisos antes de acciones críticas
window.verificarPermisosAccion = function(elemento, accion) {
    const fila = elemento.closest('tr');
    if (!fila) return true;
    
    const esAdmin = fila.querySelector('.fa-crown') !== null;
    const esMismoUsuario = fila.dataset.usuarioActual === 'true';
    
    if (esAdmin && accion !== 'ver') {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'error',
                title: '❌ Operación Denegada',
                text: 'Los usuarios Administradores están protegidos por razones de seguridad.',
                confirmButtonText: 'Entendido',
                confirmButtonColor: '#dc3545'
            });
        } else {
            alert('❌ OPERACIÓN DENEGADA: Los usuarios Administradores están protegidos por razones de seguridad.');
        }
        return false;
    }
    
    if (esMismoUsuario && (accion === 'desactivar' || accion === 'eliminar')) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'warning',
                title: '⚠️ Acción No Permitida',
                text: 'No puedes realizar esta acción en tu propio usuario.',
                confirmButtonText: 'Entendido',
                confirmButtonColor: '#ffc107'
            });
        } else {
            alert('⚠️ ACCIÓN NO PERMITIDA: No puedes realizar esta acción en tu propio usuario.');
        }
        return false;
    }
    
    return true;
};

// ✅ FUNCIÓN GLOBAL: Confirmar eliminación con protecciones
window.confirmarEliminacion = function(elemento, tipo = 'elemento') {
    const mensaje = `¿Estás seguro de que deseas eliminar este ${tipo}?`;
    const advertencia = 'Esta acción no se puede deshacer.';
    
    if (typeof Swal !== 'undefined') {
        return new Promise((resolve) => {
            Swal.fire({
                icon: 'warning',
                title: `Confirmar Eliminación`,
                text: `${mensaje}\n\n${advertencia}`,
                showCancelButton: true,
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar',
                confirmButtonColor: '#dc3545',
                cancelButtonColor: '#6c757d',
                reverseButtons: true
            }).then((result) => {
                resolve(result.isConfirmed);
            });
        });
    } else {
        return confirm(`${mensaje}\n\n${advertencia}`);
    }
};

// ✅ FUNCIÓN GLOBAL: Validar campos requeridos
window.validarCamposRequeridos = function(formulario) {
    const camposRequeridos = formulario.querySelectorAll('[required]');
    let valido = true;
    let primerCampoInvalido = null;
    
    camposRequeridos.forEach(campo => {
        if (!campo.value.trim()) {
            campo.classList.add('is-invalid');
            valido = false;
            
            if (!primerCampoInvalido) {
                primerCampoInvalido = campo;
            }
        } else {
            campo.classList.remove('is-invalid');
        }
    });
    
    if (!valido && primerCampoInvalido) {
        primerCampoInvalido.focus();
        
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'warning',
                title: 'Campos Requeridos',
                text: 'Por favor completa todos los campos obligatorios.',
                confirmButtonText: 'Entendido',
                confirmButtonColor: '#ffc107'
            });
        } else {
            alert('Por favor completa todos los campos obligatorios.');
        }
    }
    
    return valido;
};

// ✅ EVENTO GLOBAL: Prevenir envío de formularios con errores
document.addEventListener('submit', function(e) {
    const formulario = e.target;
    
    // Validar solo formularios que no sean de filtro
    if (!formulario.method || formulario.method.toLowerCase() !== 'get') {
        if (!window.validarCamposRequeridos(formulario)) {
            e.preventDefault();
            return false;
        }
    }
});

// ✅ FUNCIÓN GLOBAL: Formatear números de documento
window.formatearNumeroDocumento = function(input) {
    // Permitir solo números
    let value = input.value.replace(/\D/g, '');
    
    // Limitar a 20 caracteres máximo
    if (value.length > 20) {
        value = value.substring(0, 20);
    }
    
    input.value = value;
    
    // Disparar evento de validación
    input.dispatchEvent(new Event('input'));
};

// ✅ AUTO-APLICAR formateo a campos de documento y teléfono
document.addEventListener('input', function(e) {
    if (e.target.id === 'id_numero_documento' || e.target.name === 'numero_documento') {
        window.formatearNumeroDocumento(e.target);
    }
    if (e.target.id === 'id_telefono' || e.target.name === 'telefono') {
        window.formatearTelefono(e.target);
    }
});

// ✅ FUNCIÓN GLOBAL: Formatear números de teléfono
window.formatearTelefono = function(input) {
    // Permitir solo números
    let value = input.value.replace(/\D/g, '');
    
    // Limitar a 15 caracteres máximo
    if (value.length > 15) {
        value = value.substring(0, 15);
    }
    
    input.value = value;
    
    // Disparar evento de validación
    input.dispatchEvent(new Event('input'));
};

// ✅ MANEJO DE ERRORES GLOBALES
window.addEventListener('error', function(e) {
    console.error('Error JavaScript:', e.error);
    
    // Solo mostrar alerta en desarrollo
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.warn('Error capturado:', e.message);
    }
});

// ✅ FUNCIÓN GLOBAL: Debounce para búsquedas
window.debounce = function(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
};

// ✅ FUNCIÓN GLOBAL: Búsqueda en tiempo real
window.configurarBusquedaTiempoReal = function(inputId, callback, delay = 300) {
    const input = document.getElementById(inputId);
    if (input) {
        const busquedaDebounced = window.debounce(callback, delay);
        
        input.addEventListener('input', function(e) {
            const termino = e.target.value.trim();
            busquedaDebounced(termino);
        });
        
        // Limpiar al hacer Escape
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                e.target.value = '';
                callback('');
            }
        });
    }
};

// ✅ FUNCIÓN GLOBAL: Mostrar/ocultar contraseña
window.togglePassword = function(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    
    if (input && icon) {
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    }
};

// ✅ FUNCIÓN GLOBAL: Copiar al portapapeles
window.copiarAlPortapapeles = function(texto, mensaje = 'Copiado al portapapeles') {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(texto).then(() => {
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    icon: 'success',
                    title: mensaje,
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 2000
                });
            } else {
                alert(mensaje);
            }
        }).catch(err => {
            console.error('Error al copiar:', err);
        });
    } else {
        // Fallback para navegadores antiguos
        const textArea = document.createElement('textarea');
        textArea.value = texto;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            textArea.remove();
            alert(mensaje);
        } catch (err) {
            console.error('Error al copiar:', err);
            textArea.remove();
        }
    }
};

// ✅ FUNCIÓN GLOBAL: Validar email
window.validarEmail = function(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
};

// ✅ FUNCIÓN GLOBAL: Validar teléfono
window.validarTelefono = function(telefono) {
    const regex = /^[\+]?[1-9][\d]{0,15}$/;
    return regex.test(telefono.replace(/\s/g, ''));
};

// ✅ FUNCIÓN GLOBAL: Formatear fecha para mostrar
window.formatearFecha = function(fecha, formato = 'dd/mm/yyyy') {
    if (!fecha) return '';
    
    const date = new Date(fecha);
    if (isNaN(date.getTime())) return fecha;
    
    const dia = String(date.getDate()).padStart(2, '0');
    const mes = String(date.getMonth() + 1).padStart(2, '0');
    const año = date.getFullYear();
    
    switch (formato.toLowerCase()) {
        case 'dd/mm/yyyy':
            return `${dia}/${mes}/${año}`;
        case 'mm/dd/yyyy':
            return `${mes}/${dia}/${año}`;
        case 'yyyy-mm-dd':
            return `${año}-${mes}-${dia}`;
        default:
            return date.toLocaleDateString();
    }
};

// ✅ FUNCIÓN GLOBAL: Formatear moneda
window.formatearMoneda = function(cantidad, moneda = 'BOB') {
    if (isNaN(cantidad)) return '0.00';
    
    return new Intl.NumberFormat('es-BO', {
        style: 'currency',
        currency: moneda,
        minimumFractionDigits: 2
    }).format(cantidad);
};

// ✅ FUNCIÓN GLOBAL: Detectar dispositivo móvil
window.esMobile = function() {
    return window.innerWidth <= 768 || /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
};

// ✅ FUNCIÓN GLOBAL: Scroll suave a elemento
window.scrollToElement = function(elementId, offset = 0) {
    const element = document.getElementById(elementId);
    if (element) {
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - offset;
        
        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }
};

// ✅ FUNCIÓN GLOBAL: Generar ID único
window.generarIdUnico = function(prefijo = 'id') {
    return `${prefijo}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

// ✅ FUNCIÓN GLOBAL: Capitalizar texto
window.capitalize = function(texto) {
    if (!texto) return '';
    return texto.charAt(0).toUpperCase() + texto.slice(1).toLowerCase();
};

// ✅ FUNCIÓN GLOBAL: Limpiar texto
window.limpiarTexto = function(texto) {
    if (!texto) return '';
    return texto.trim().replace(/\s+/g, ' ');
};

// ✅ FUNCIÓN GLOBAL: Validar formulario completo
window.validarFormulario = function(formulario) {
    let esValido = true;
    const errores = [];
    
    // Validar campos requeridos
    const camposRequeridos = formulario.querySelectorAll('[required]');
    camposRequeridos.forEach(campo => {
        if (!campo.value.trim()) {
            campo.classList.add('is-invalid');
            errores.push(`El campo ${campo.name || campo.id} es requerido`);
            esValido = false;
        } else {
            campo.classList.remove('is-invalid');
        }
    });
    
    // Validar emails
    const camposEmail = formulario.querySelectorAll('input[type="email"]');
    camposEmail.forEach(campo => {
        if (campo.value && !window.validarEmail(campo.value)) {
            campo.classList.add('is-invalid');
            errores.push(`El email ${campo.value} no es válido`);
            esValido = false;
        }
    });
    
    // Validar teléfonos
    const camposTelefono = formulario.querySelectorAll('input[type="tel"]');
    camposTelefono.forEach(campo => {
        if (campo.value && !window.validarTelefono(campo.value)) {
            campo.classList.add('is-invalid');
            errores.push(`El teléfono ${campo.value} no es válido`);
            esValido = false;
        }
    });
    
    // Validar números de documento
    const camposDocumento = formulario.querySelectorAll('input[name="numero_documento"]');
    camposDocumento.forEach(campo => {
        if (campo.value) {
            const soloNumeros = /^\d+$/.test(campo.value);
            if (!soloNumeros || campo.value.length < 7) {
                campo.classList.add('is-invalid');
                errores.push('El número de documento debe tener al menos 7 dígitos numéricos');
                esValido = false;
            }
        }
    });
    
    if (!esValido && errores.length > 0) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'error',
                title: 'Errores en el formulario',
                html: errores.map(error => `• ${error}`).join('<br>'),
                confirmButtonText: 'Corregir',
                confirmButtonColor: '#dc3545'
            });
        } else {
            alert('Errores en el formulario:\n' + errores.join('\n'));
        }
    }
    
    return esValido;
};

// ✅ APLICAR VALIDACIONES AUTOMÁTICAS
document.addEventListener('DOMContentLoaded', function() {
    // Auto-validar formularios al enviar
    const formularios = document.querySelectorAll('form:not([method="GET"])');
    formularios.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!window.validarFormulario(this)) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Auto-validar campos en tiempo real
    document.addEventListener('blur', function(e) {
        const campo = e.target;
        
        // Validar email
        if (campo.type === 'email' && campo.value) {
            if (window.validarEmail(campo.value)) {
                campo.classList.remove('is-invalid');
                campo.classList.add('is-valid');
            } else {
                campo.classList.remove('is-valid');
                campo.classList.add('is-invalid');
            }
        }
        
        // Validar teléfono
        if (campo.type === 'tel' && campo.value) {
            if (window.validarTelefono(campo.value)) {
                campo.classList.remove('is-invalid');
                campo.classList.add('is-valid');
            } else {
                campo.classList.remove('is-valid');
                campo.classList.add('is-invalid');
            }
        }
        
        // Validar campos requeridos
        if (campo.hasAttribute('required')) {
            if (campo.value.trim()) {
                campo.classList.remove('is-invalid');
                campo.classList.add('is-valid');
            } else {
                campo.classList.remove('is-valid');
                campo.classList.add('is-invalid');
            }
        }
    }, true);
});

// ✅ CONFIGURACIÓN GLOBAL PARA DESARROLLO
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    // Consola de desarrollo
    console.log('🚀 Torre Segura - Modo Desarrollo');
    console.log('📝 Scripts cargados correctamente');
    console.log('🛡️ Protecciones de seguridad activas');
    
    // Funciones de desarrollo
    window.dev = {
        mostrarProtecciones: function() {
            console.log('🛡️ Protecciones activas:');
            console.log('- Usuarios Administradores protegidos');
            console.log('- Validación de documentos');
            console.log('- Confirmaciones de acciones críticas');
            console.log('- Validaciones de formulario en tiempo real');
        },
        simularError: function() {
            throw new Error('Error simulado para pruebas');
        },
        mostrarElementosProtegidos: function() {
            const elementosProtegidos = document.querySelectorAll('[class*="admin"], .fa-crown, .disabled');
            console.log(`Encontrados ${elementosProtegidos.length} elementos protegidos:`, elementosProtegidos);
        }
    };
}

// ✅ MENSAJE DE CONFIRMACIÓN DE CARGA
console.log('✅ Torre Segura - Scripts cargados completamente');
console.log('🔒 Sistema de protección de usuarios Administradores: ACTIVO');
console.log('📱 Optimizaciones móviles: ACTIVAS');
console.log('🎯 Validaciones en tiempo real: ACTIVAS');