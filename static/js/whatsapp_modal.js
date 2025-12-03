// static/js/whatsapp_modal.js
// Sistema de mensajes de WhatsApp con plantillas editables

// Plantillas de mensajes predefinidas
const whatsappTemplates = {
    cita: {
        nombre: 'Recordatorio de Cita',
        icono: 'bi-calendar-check',
        mensaje: `Hola {nombre}, te recordamos tu cita el {fecha} a las {hora} en {consultorio}. ¡Te esperamos! 😊`
    },
    pago: {
        nombre: 'Recordatorio de Pago',
        icono: 'bi-cash-coin',
        mensaje: `Hola {nombre}, tienes un saldo pendiente de S/ {monto} por el tratamiento de {tratamiento}. Puedes realizar el pago en nuestro consultorio. Gracias 💳`
    },
    cumpleanos: {
        nombre: 'Felicitación de Cumpleaños',
        icono: 'bi-cake2',
        mensaje: `¡Feliz cumpleaños {nombre}! 🎉🎂 El equipo de {consultorio} te desea un día maravilloso lleno de alegría y salud.`
    },
    confirmacion: {
        nombre: 'Confirmación de Cita',
        icono: 'bi-check-circle',
        mensaje: `Hola {nombre}, ¿confirmas tu asistencia para la cita del {fecha} a las {hora}? Por favor responde SÍ o NO. Gracias 📅`
    },
    personalizado: {
        nombre: 'Mensaje Personalizado',
        icono: 'bi-chat-dots',
        mensaje: `Hola {nombre}, `
    }
};

// Datos del paciente actual (se llenarán desde el template)
let pacienteData = {};

/**
 * Inicializar el modal de WhatsApp
 * @param {Object} data - Datos del paciente
 */
function initWhatsAppModal(data) {
    pacienteData = data;
    
    // Cargar plantillas en el selector
    const templateSelect = document.getElementById('whatsappTemplateSelect');
    if (templateSelect) {
        templateSelect.innerHTML = '';
        
        Object.keys(whatsappTemplates).forEach(key => {
            const template = whatsappTemplates[key];
            const option = document.createElement('option');
            option.value = key;
            option.textContent = template.nombre;
            templateSelect.appendChild(option);
        });
        
        // Cargar la primera plantilla por defecto
        loadTemplate(Object.keys(whatsappTemplates)[0]);
    }
}

/**
 * Cargar una plantilla en el editor
 * @param {string} templateKey - Clave de la plantilla
 */
function loadTemplate(templateKey) {
    const template = whatsappTemplates[templateKey];
    if (!template) return;
    
    // Reemplazar variables en el mensaje
    let mensaje = template.mensaje;
    mensaje = replaceVariables(mensaje, pacienteData);
    
    // Actualizar el textarea
    const messageArea = document.getElementById('whatsappMessage');
    if (messageArea) {
        messageArea.value = mensaje;
        updateCharCount();
    }
    
    // Actualizar el icono del modal
    const modalIcon = document.getElementById('whatsappModalIcon');
    if (modalIcon) {
        modalIcon.className = `bi ${template.icono} me-2`;
    }
}

/**
 * Reemplazar variables en el mensaje
 * @param {string} mensaje - Mensaje con variables
 * @param {Object} data - Datos para reemplazar
 * @returns {string} Mensaje con variables reemplazadas
 */
function replaceVariables(mensaje, data) {
    return mensaje
        .replace(/{nombre}/g, data.nombre || '[Nombre]')
        .replace(/{fecha}/g, data.fecha || '[Fecha]')
        .replace(/{hora}/g, data.hora || '[Hora]')
        .replace(/{monto}/g, data.monto || '[Monto]')
        .replace(/{tratamiento}/g, data.tratamiento || '[Tratamiento]')
        .replace(/{consultorio}/g, data.consultorio || 'Consultorio Dental');
}

/**
 * Limpiar número de teléfono
 * @param {string} telefono - Número de teléfono
 * @returns {string} Número limpio
 */
function cleanPhoneNumber(telefono) {
    if (!telefono) return '';
    
    // Quitar espacios, guiones, paréntesis, etc.
    let cleaned = telefono.replace(/[\s\-\(\)]/g, '');
    
    // Si empieza con +51, quitarlo
    if (cleaned.startsWith('+51')) {
        cleaned = cleaned.substring(3);
    }
    
    // Si empieza con 51, quitarlo
    if (cleaned.startsWith('51') && cleaned.length > 9) {
        cleaned = cleaned.substring(2);
    }
    
    return cleaned;
}

/**
 * Validar número de teléfono peruano
 * @param {string} telefono - Número de teléfono
 * @returns {boolean} True si es válido
 */
function validatePhoneNumber(telefono) {
    const cleaned = cleanPhoneNumber(telefono);
    
    // Debe tener 9 dígitos y empezar con 9
    return /^9\d{8}$/.test(cleaned);
}

/**
 * Generar URL de WhatsApp
 * @param {string} telefono - Número de teléfono
 * @param {string} mensaje - Mensaje a enviar
 * @returns {string} URL de WhatsApp
 */
function generateWhatsAppURL(telefono, mensaje) {
    const cleaned = cleanPhoneNumber(telefono);
    const encoded = encodeURIComponent(mensaje);
    
    // Formato: https://wa.me/51XXXXXXXXX?text=mensaje
    return `https://wa.me/51${cleaned}?text=${encoded}`;
}

/**
 * Enviar mensaje por WhatsApp
 */
function sendWhatsAppMessage() {
    const telefono = pacienteData.telefono;
    const mensaje = document.getElementById('whatsappMessage').value;
    
    // Validar que haya teléfono
    if (!telefono) {
        showAlert('El paciente no tiene número de teléfono registrado.', 'warning');
        return;
    }
    
    // Validar formato del teléfono
    if (!validatePhoneNumber(telefono)) {
        showAlert('El número de teléfono no es válido. Debe ser un número peruano de 9 dígitos.', 'warning');
        return;
    }
    
    // Validar que haya mensaje
    if (!mensaje.trim()) {
        showAlert('Por favor escribe un mensaje.', 'warning');
        return;
    }
    
    // Generar URL y abrir WhatsApp
    const url = generateWhatsAppURL(telefono, mensaje);
    window.open(url, '_blank');
    
    // Cerrar el modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('whatsappModal'));
    if (modal) {
        modal.hide();
    }
    
    showAlert('WhatsApp se abrió en una nueva ventana. Envía el mensaje desde allí.', 'success');
}

/**
 * Actualizar contador de caracteres
 */
function updateCharCount() {
    const messageArea = document.getElementById('whatsappMessage');
    const charCount = document.getElementById('charCount');
    
    if (messageArea && charCount) {
        const length = messageArea.value.length;
        charCount.textContent = `${length} caracteres`;
        
        // Cambiar color si es muy largo
        if (length > 1000) {
            charCount.classList.add('text-danger');
        } else {
            charCount.classList.remove('text-danger');
        }
    }
}

/**
 * Mostrar alerta
 * @param {string} message - Mensaje
 * @param {string} type - Tipo de alerta (success, warning, danger, info)
 */
function showAlert(message, type = 'info') {
    // Crear elemento de alerta
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-cerrar después de 5 segundos
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Cambio de plantilla
    const templateSelect = document.getElementById('whatsappTemplateSelect');
    if (templateSelect) {
        templateSelect.addEventListener('change', function() {
            loadTemplate(this.value);
        });
    }
    
    // Actualizar contador de caracteres
    const messageArea = document.getElementById('whatsappMessage');
    if (messageArea) {
        messageArea.addEventListener('input', updateCharCount);
    }
    
    // Botón de enviar
    const sendBtn = document.getElementById('sendWhatsAppBtn');
    if (sendBtn) {
        sendBtn.addEventListener('click', sendWhatsAppMessage);
    }
});
