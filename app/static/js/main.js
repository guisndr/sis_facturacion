document.addEventListener('DOMContentLoaded', function() {
    // Cerrar alerts después de 5s
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    });

    // Confirm para deletes
    document.querySelectorAll('form[action*="eliminar"]').forEach(form => {
        form.addEventListener('submit', e => {
            if (!confirm('¿Seguro que quieres eliminar?')) {
                e.preventDefault();
            }
        });
    });

    // Format currency para inputs (si usas class="currency-input")
    document.querySelectorAll('.currency-input').forEach(input => {
        input.addEventListener('input', function() {
            let value = this.value.replace(/[^0-9.]/g, '');
            let parts = value.split('.');
            if (parts.length > 2) value = parts[0] + '.' + parts.slice(1).join('');
            if (parts[1] && parts[1].length > 2) parts[1] = parts[1].substring(0, 2);
            this.value = parts.join('.');
        });
    });

    // Inicializar funcionalidades avanzadas
    initializeTooltips();
    initializeModals();
    initializeForms();
    initializeTables();
    initializeNotifications();
    initializeSearch();
    initializeFilters();
});

// Tooltips
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const element = event.target;
    const tooltipText = element.getAttribute('title') || element.getAttribute('data-bs-title');

    if (!tooltipText) return;

    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip-text';
    tooltip.textContent = tooltipText;
    document.body.appendChild(tooltip);

    const rect = element.getBoundingClientRect();
    tooltip.style.left = (rect.left + rect.width / 2) + 'px';
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';

    element._tooltip = tooltip;
    setTimeout(() => tooltip.classList.add('show'), 10);
}

function hideTooltip(event) {
    const element = event.target;
    const tooltip = element._tooltip;
    if (tooltip) {
        tooltip.classList.remove('show');
        setTimeout(() => {
            if (tooltip.parentNode) {
                tooltip.parentNode.removeChild(tooltip);
            }
        }, 150);
        delete element._tooltip;
    }
}

// Modales
function initializeModals() {
    const modalTriggers = document.querySelectorAll('[data-bs-toggle="modal"]');
    const closeButtons = document.querySelectorAll('[data-bs-dismiss="modal"]');

    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('data-bs-target');
            const modal = document.querySelector(targetId);
            if (modal) {
                showModal(modal);
            }
        });
    });

    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                hideModal(modal);
            }
        });
    });

    // Cerrar modal al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            hideModal(e.target);
        }
    });
}

function showModal(modal) {
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';

    // Trigger animation
    setTimeout(() => {
        modal.classList.add('show');
        const modalContent = modal.querySelector('.modal-container, .modal-content');
        if (modalContent) {
            modalContent.classList.add('fade-in-up');
        }
    }, 10);
}

function hideModal(modal) {
    modal.classList.remove('show');
    document.body.style.overflow = '';

    setTimeout(() => {
        modal.style.display = 'none';
        const modalContent = modal.querySelector('.modal-container, .modal-content');
        if (modalContent) {
            modalContent.classList.remove('fade-in-up');
        }
    }, 300);
}

// Formularios
function initializeForms() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);

        // Validación en tiempo real
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', validateField);
            input.addEventListener('input', clearFieldError);
        });
    });
}

function handleFormSubmit(e) {
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading-spinner"></span> Procesando...';
    }

    // Aquí puedes agregar lógica adicional de validación
    // o envío AJAX si es necesario
}

function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    const fieldGroup = field.closest('.form-group, .input-group');

    // Limpiar errores anteriores
    clearFieldError(e);

    // Validaciones básicas
    let isValid = true;
    let errorMessage = '';

    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'Este campo es requerido';
    } else if (field.type === 'email' && value && !isValidEmail(value)) {
        isValid = false;
        errorMessage = 'Ingrese un email válido';
    } else if (field.type === 'number' && value && isNaN(value)) {
        isValid = false;
        errorMessage = 'Ingrese un número válido';
    }

    if (!isValid) {
        showFieldError(fieldGroup, errorMessage);
    }

    return isValid;
}

function showFieldError(fieldGroup, message) {
    fieldGroup.classList.add('error');

    let errorElement = fieldGroup.querySelector('.invalid-feedback');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        fieldGroup.appendChild(errorElement);
    }

    errorElement.textContent = message;
}

function clearFieldError(e) {
    const field = e.target;
    const fieldGroup = field.closest('.form-group, .input-group');

    fieldGroup.classList.remove('error');

    const errorElement = fieldGroup.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Tablas
function initializeTables() {
    const tables = document.querySelectorAll('.table-responsive');

    tables.forEach(table => {
        // Agregar funcionalidad de ordenamiento
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(table, this.dataset.sort, this.dataset.sortType || 'string');
            });
        });
    });
}

function sortTable(table, column, type) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.rows);
    const header = table.querySelector(`th[data-sort="${column}"]`);
    const isAscending = header.classList.contains('sort-asc');

    // Remover clases de ordenamiento anteriores
    table.querySelectorAll('th.sort-asc, th.sort-desc').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });

    // Agregar clase de ordenamiento
    header.classList.add(isAscending ? 'sort-desc' : 'sort-asc');

    rows.sort((a, b) => {
        const aValue = a.cells[Array.from(a.cells).findIndex(cell =>
            cell.dataset.column === column)].textContent.trim();
        const bValue = b.cells[Array.from(b.cells).findIndex(cell =>
            cell.dataset.column === column)].textContent.trim();

        if (type === 'number') {
            return isAscending ? bValue - aValue : aValue - bValue;
        } else if (type === 'date') {
            return isAscending ?
                new Date(bValue) - new Date(aValue) :
                new Date(aValue) - new Date(bValue);
        } else {
            return isAscending ?
                bValue.localeCompare(aValue) :
                aValue.localeCompare(bValue);
        }
    });

    rows.forEach(row => tbody.appendChild(row));
}

// Notificaciones
function initializeNotifications() {
    const notifications = document.querySelectorAll('.notification-item');

    notifications.forEach(notification => {
        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            hideNotification(notification);
        }, 5000);

        // Botón de cerrar
        const closeBtn = notification.querySelector('.btn-close, .close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                hideNotification(notification);
            });
        }
    });
}

function hideNotification(notification) {
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(100%)';

    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

// Búsqueda
function initializeSearch() {
    const searchInputs = document.querySelectorAll('input[data-search]');

    searchInputs.forEach(input => {
        let searchTimeout;

        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            const targetTable = document.querySelector(this.dataset.search);

            searchTimeout = setTimeout(() => {
                if (query.length >= 2 || query.length === 0) {
                    performSearch(targetTable, query);
                }
            }, 300);
        });
    });
}

function performSearch(table, query) {
    if (!table) return;

    const rows = table.querySelectorAll('tbody tr');
    const searchTerms = query.toLowerCase().split(' ').filter(term => term.length > 0);

    rows.forEach(row => {
        if (searchTerms.length === 0) {
            row.style.display = '';
            return;
        }

        const text = row.textContent.toLowerCase();
        const matches = searchTerms.every(term => text.includes(term));

        row.style.display = matches ? '' : 'none';
    });
}

// Filtros
function initializeFilters() {
    const filterSelects = document.querySelectorAll('select[data-filter]');

    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            const filterValue = this.value;
            const targetTable = document.querySelector(this.dataset.filter);
            applyFilter(targetTable, this.dataset.filterColumn, filterValue);
        });
    });
}

function applyFilter(table, column, value) {
    if (!table) return;

    const rows = table.querySelectorAll('tbody tr');

    rows.forEach(row => {
        if (value === 'all' || value === '') {
            row.style.display = '';
            return;
        }

        const cell = row.cells[Array.from(row.cells).findIndex(cell =>
            cell.dataset.column === column)];
        const cellValue = cell ? cell.textContent.trim() : '';

        row.style.display = cellValue === value ? '' : 'none';
    });
}

// Función para format currency (usar en templates si necesitas)
function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2);
}

// Utilidades adicionales
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatNumber(number) {
    return new Intl.NumberFormat('es-ES').format(number);
}

function formatDate(date) {
    return new Date(date).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

// Confirmación de acciones
function confirmAction(message = '¿Está seguro de que desea continuar?') {
    return confirm(message);
}

// Copiar al portapapeles
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Texto copiado al portapapeles', 'success');
        });
    } else {
        // Fallback para navegadores antiguos
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Texto copiado al portapapeles', 'success');
    }
}

// Mostrar notificación
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification-item ${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button class="btn-close" onclick="hideNotification(this.parentNode)">×</button>
    `;

    let container = document.querySelector('.notifications-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'notifications-container';
        document.body.appendChild(container);
    }

    container.appendChild(notification);
    initializeNotifications();
}

// AJAX helper
function ajaxRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };

    if (options.body && typeof options.body === 'object') {
        options.body = JSON.stringify(options.body);
    }

    return fetch(url, { ...defaultOptions, ...options })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('AJAX Error:', error);
            showNotification('Error en la solicitud', 'error');
            throw error;
        });
}

// Exportar funciones globales
window.AppUtils = {
    formatCurrency,
    formatDate,
    formatNumber,
    confirmAction,
    copyToClipboard,
    showNotification,
    ajaxRequest,
    debounce
};