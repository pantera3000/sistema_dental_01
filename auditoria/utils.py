# auditoria/utils.py
# Utilidades para registrar logs de auditoría

from .models import LogAuditoria


def registrar_log(usuario, accion, modelo, objeto_id=None, objeto_repr='', cambios=None, detalles='', request=None):
    """
    Función helper para registrar logs de auditoría
    
    Args:
        usuario: Usuario que realiza la acción
        accion: Tipo de acción (CREAR, EDITAR, ELIMINAR, etc.)
        modelo: Nombre del modelo afectado
        objeto_id: ID del objeto (opcional)
        objeto_repr: Representación del objeto (opcional)
        cambios: Dict con cambios antes/después (opcional)
        detalles: Información adicional (opcional)
        request: Request object para obtener IP (opcional)
    """
    ip_address = None
    user_agent = ''
    
    if request:
        # Obtener IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Obtener User Agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
    
    LogAuditoria.objects.create(
        usuario=usuario,
        accion=accion,
        modelo=modelo,
        objeto_id=objeto_id,
        objeto_repr=objeto_repr,
        cambios=cambios,
        detalles=detalles,
        ip_address=ip_address,
        user_agent=user_agent
    )
