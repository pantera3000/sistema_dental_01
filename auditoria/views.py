# auditoria/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import LogAuditoria
from datetime import datetime, timedelta


def es_admin_o_superuser(user):
    """Verifica si el usuario es superusuario o pertenece al grupo Administrador"""
    return user.is_superuser or user.groups.filter(name='Administrador').exists()


@user_passes_test(es_admin_o_superuser, login_url='/dashboard/')
def logs_sistema(request):
    """Vista principal de logs de auditoría"""
    
    # Obtener filtros
    filtro_usuario = request.GET.get('usuario', '')
    filtro_accion = request.GET.get('accion', '')
    filtro_modelo = request.GET.get('modelo', '')
    filtro_fecha_desde = request.GET.get('fecha_desde', '')
    filtro_fecha_hasta = request.GET.get('fecha_hasta', '')
    busqueda = request.GET.get('q', '')
    
    # Query base
    logs = LogAuditoria.objects.all()
    
    # Aplicar filtros
    if filtro_usuario:
        logs = logs.filter(usuario__id=filtro_usuario)
    
    if filtro_accion:
        logs = logs.filter(accion=filtro_accion)
    
    if filtro_modelo:
        logs = logs.filter(modelo=filtro_modelo)
    
    if filtro_fecha_desde:
        try:
            fecha_desde = datetime.strptime(filtro_fecha_desde, '%Y-%m-%d')
            logs = logs.filter(fecha_hora__gte=fecha_desde)
        except ValueError:
            pass
    
    if filtro_fecha_hasta:
        try:
            fecha_hasta = datetime.strptime(filtro_fecha_hasta, '%Y-%m-%d')
            fecha_hasta = fecha_hasta.replace(hour=23, minute=59, second=59)
            logs = logs.filter(fecha_hora__lte=fecha_hasta)
        except ValueError:
            pass
    
    # Búsqueda de texto
    if busqueda:
        logs = logs.filter(
            Q(usuario_nombre__icontains=busqueda) |
            Q(objeto_repr__icontains=busqueda) |
            Q(detalles__icontains=busqueda) |
            Q(ip_address__icontains=busqueda)
        )
    
    # Estadísticas
    total_logs = logs.count()
    logs_hoy = logs.filter(fecha_hora__gte=datetime.now().replace(hour=0, minute=0, second=0)).count()
    logs_semana = logs.filter(fecha_hora__gte=datetime.now() - timedelta(days=7)).count()
    
    # Acciones más comunes
    acciones_stats = logs.values('accion').annotate(total=Count('id')).order_by('-total')[:5]
    
    # Paginación
    paginator = Paginator(logs, 50)  # 50 logs por página
    page_number = request.GET.get('page')
    logs_paginados = paginator.get_page(page_number)
    
    # Obtener listas para filtros
    from django.contrib.auth.models import User
    usuarios = User.objects.filter(logs_auditoria__isnull=False).distinct()
    modelos_unicos = LogAuditoria.objects.values_list('modelo', flat=True).distinct().order_by('modelo')
    
    context = {
        'logs': logs_paginados,
        'total_logs': total_logs,
        'logs_hoy': logs_hoy,
        'logs_semana': logs_semana,
        'acciones_stats': acciones_stats,
        'usuarios': usuarios,
        'modelos_unicos': modelos_unicos,
        'acciones_choices': LogAuditoria.ACCION_CHOICES,
        # Filtros actuales
        'filtro_usuario': filtro_usuario,
        'filtro_accion': filtro_accion,
        'filtro_modelo': filtro_modelo,
        'filtro_fecha_desde': filtro_fecha_desde,
        'filtro_fecha_hasta': filtro_fecha_hasta,
        'busqueda': busqueda,
    }
    
    return render(request, 'auditoria/logs.html', context)
