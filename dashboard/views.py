# dashboard/views.py

from django.shortcuts import render
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal

from pacientes.models import Paciente
from tratamientos.models import Tratamiento, Pago
from historias.models import EntradaHistoria
from notas.models import Nota


def dashboard_view(request):
    """Vista principal del dashboard con métricas clave"""
    
    # Fechas de referencia
    now = timezone.now()
    inicio_mes = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    fin_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
    hace_6_meses = now - timedelta(days=180)
    inicio_semana = now - timedelta(days=now.weekday())
    
    # ============ KPIs PRINCIPALES ============
    
    # 1. Total Pacientes Activos (con citas/tratamientos en últimos 6 meses)
    pacientes_activos = Paciente.objects.filter(
        Q(tratamientos__fecha_inicio__gte=hace_6_meses) |
        Q(entradas_historia__fecha__gte=hace_6_meses)
    ).distinct().count()
    
    # 2. Ingresos del Mes
    ingresos_mes = Pago.objects.filter(
        fecha_pago__gte=inicio_mes,
        fecha_pago__lte=fin_mes
    ).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
    
    # 3. Tratamientos Activos (en progreso)
    tratamientos_activos = Tratamiento.objects.filter(
        estado='en_progreso'
    ).count()
    
    # 4. Deuda Total
    tratamientos_con_deuda = Tratamiento.objects.annotate(
        suma_pagos=Sum('pagos__monto')
    ).filter(
        Q(suma_pagos__lt=F('costo_total')) | Q(suma_pagos__isnull=True)
    )
    
    deuda_total = sum([
        (t.costo_total - (t.pagos.aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')))
        for t in tratamientos_con_deuda
    ])
    
    # 5. Citas de esta semana (desde Google Calendar)
    from citas.utils import get_calendar_events
    import pytz
    
    # Obtener todos los eventos
    all_events = get_calendar_events()
    
    # Configurar fechas para filtro de semana
    limatz = pytz.timezone('America/Lima')
    now_lima = now.astimezone(limatz)
    start_week = now_lima - timedelta(days=now_lima.weekday())
    start_week = start_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_week = start_week + timedelta(days=7)
    
    citas_semana = 0
    proximas_citas = []
    
    for event in all_events:
        # Contar citas de esta semana
        if start_week <= event.local_begin < end_week:
            citas_semana += 1
            
        # Recopilar próximas citas (futuras)
        if event.local_begin >= now_lima:
            proximas_citas.append(event)
            
    # Limitar próximas citas a 5
    proximas_citas = proximas_citas[:5]

    # 6. Tasa de Cobro (%)
    total_facturado = Tratamiento.objects.aggregate(
        total=Sum('costo_total')
    )['total'] or Decimal('0.00')
    
    total_cobrado = Pago.objects.aggregate(
        total=Sum('monto')
    )['total'] or Decimal('0.00')
    
    tasa_cobro = (total_cobrado / total_facturado * 100) if total_facturado > 0 else 0

    # ============ LISTAS RÁPIDAS ============
    
    # Pacientes con mayor deuda
    pacientes_deuda = []
    for t in tratamientos_con_deuda.select_related('paciente')[:10]:
        pagado = t.pagos.aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')
        deuda = t.costo_total - pagado
        if deuda > 0:
            pacientes_deuda.append({
                'paciente': t.paciente,
                'tratamiento': t,
                'deuda': deuda
            })
    
    pacientes_deuda = sorted(pacientes_deuda, key=lambda x: x['deuda'], reverse=True)[:5]
    
    # Últimos tratamientos creados
    ultimos_tratamientos = Tratamiento.objects.select_related('paciente').order_by('-fecha_inicio')[:5]
    
    # Cumpleaños próximos (próximos 30 días)
    hoy = now.date()
    cumpleanos_proximos = Paciente.objects.filter(
        fecha_nacimiento__month__gte=hoy.month
    ).order_by('fecha_nacimiento__month', 'fecha_nacimiento__day')[:5]
    
    # ============ DATOS PARA GRÁFICOS ============
    
    # Gráfico 1: Ingresos por mes (últimos 6 meses)
    ingresos_mensuales = []
    meses_labels = []
    
    for i in range(5, -1, -1):
        mes_inicio = (now.replace(day=1) - timedelta(days=i*30)).replace(day=1, hour=0, minute=0, second=0)
        mes_fin = (mes_inicio + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        ingreso = Pago.objects.filter(
            fecha_pago__gte=mes_inicio,
            fecha_pago__lte=mes_fin
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
        
        ingresos_mensuales.append(float(ingreso))
        meses_labels.append(mes_inicio.strftime('%b %Y'))
    
    # Gráfico 2: Tratamientos por estado
    tratamientos_stats = {
        'en_progreso': Tratamiento.objects.filter(estado='en_progreso').count(),
        'completado': Tratamiento.objects.filter(estado='completado').count(),
        'pendiente': Tratamiento.objects.filter(estado='pendiente').count(),
    }
    
    # Gráfico 3: Métodos de pago
    metodos_pago = Pago.objects.values('metodo_pago').annotate(
        total=Sum('monto'),
        cantidad=Count('id')
    ).order_by('-total')
    
    # Gráfico 4: Pacientes nuevos por mes (últimos 6 meses)
    pacientes_nuevos_mes = []
    
    for i in range(5, -1, -1):
        mes_inicio = (now.replace(day=1) - timedelta(days=i*30)).replace(day=1, hour=0, minute=0, second=0)
        mes_fin = (mes_inicio + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        nuevos = Paciente.objects.filter(
            creado_en__gte=mes_inicio,
            creado_en__lte=mes_fin
        ).count()
        
        pacientes_nuevos_mes.append(nuevos)
    
    context = {
        # KPIs
        'pacientes_activos': pacientes_activos,
        'ingresos_mes': ingresos_mes,
        'tratamientos_activos': tratamientos_activos,
        'deuda_total': deuda_total,
        'citas_semana': citas_semana,
        'tasa_cobro': round(tasa_cobro, 1),
        
        # Gráficos
        'ingresos_mensuales': ingresos_mensuales,
        'meses_labels': meses_labels,
        'tratamientos_stats': tratamientos_stats,
        'metodos_pago': metodos_pago,
        'pacientes_nuevos_mes': pacientes_nuevos_mes,
        
        # Listas
        'proximas_citas': proximas_citas,
        'pacientes_deuda': pacientes_deuda,
        'ultimos_tratamientos': ultimos_tratamientos,
        'cumpleanos_proximos': cumpleanos_proximos,
    }
    
    return render(request, 'dashboard/index.html', context)


def estadisticas_view(request):
    """Vista para reportes y gráficos estadísticos con filtros"""
    now = timezone.now()
    
    # Obtener año seleccionado (por defecto el actual)
    año_seleccionado = int(request.GET.get('año', now.year))
    
    # ============ GRÁFICO 1: Ingresos por Mes (Año Seleccionado) ============
    ingresos_mensuales = []
    meses_labels = []
    
    for mes in range(1, 13):
        mes_inicio = timezone.make_aware(datetime(año_seleccionado, mes, 1))
        if mes == 12:
            mes_fin = timezone.make_aware(datetime(año_seleccionado + 1, 1, 1)) - timedelta(seconds=1)
        else:
            mes_fin = timezone.make_aware(datetime(año_seleccionado, mes + 1, 1)) - timedelta(seconds=1)
        
        ingreso = Pago.objects.filter(
            fecha_pago__gte=mes_inicio,
            fecha_pago__lte=mes_fin
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
        
        ingresos_mensuales.append(float(ingreso))
        meses_labels.append(mes_inicio.strftime('%B'))  # Nombre del mes
    
    # ============ GRÁFICO 2: Tratamientos Más Comunes (Top 10) ============
    top_tratamientos = Tratamiento.objects.values('descripcion').annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    tratamientos_labels = [t['descripcion'] for t in top_tratamientos]
    tratamientos_data = [t['total'] for t in top_tratamientos]
    
    # ============ GRÁFICO 3: Pacientes Nuevos vs Recurrentes ============
    # Pacientes nuevos por mes
    pacientes_nuevos_mes = []
    pacientes_recurrentes_mes = []
    
    for mes in range(1, 13):
        mes_inicio = timezone.make_aware(datetime(año_seleccionado, mes, 1))
        if mes == 12:
            mes_fin = timezone.make_aware(datetime(año_seleccionado + 1, 1, 1)) - timedelta(seconds=1)
        else:
            mes_fin = timezone.make_aware(datetime(año_seleccionado, mes + 1, 1)) - timedelta(seconds=1)
        
        # Pacientes nuevos: creados en este mes
        nuevos = Paciente.objects.filter(
            creado_en__gte=mes_inicio,
            creado_en__lte=mes_fin
        ).count()
        
        # Pacientes recurrentes: tienen tratamientos en este mes pero fueron creados antes
        recurrentes = Tratamiento.objects.filter(
            fecha_inicio__gte=mes_inicio,
            fecha_inicio__lte=mes_fin,
            paciente__creado_en__lt=mes_inicio
        ).values('paciente').distinct().count()
        
        pacientes_nuevos_mes.append(nuevos)
        pacientes_recurrentes_mes.append(recurrentes)
    
    # ============ GRÁFICO 4: Tasa de Completación de Tratamientos ============
    total_tratamientos = Tratamiento.objects.count()
    
    completados = Tratamiento.objects.filter(estado='completado').count()
    en_progreso = Tratamiento.objects.filter(estado='en_progreso').count()
    pendientes = Tratamiento.objects.filter(estado='pendiente').count()
    cancelados = Tratamiento.objects.filter(estado='cancelado').count() if Tratamiento.objects.filter(estado='cancelado').exists() else 0
    
    # Calcular porcentajes
    if total_tratamientos > 0:
        porcentaje_completado = round((completados / total_tratamientos) * 100, 1)
        porcentaje_en_progreso = round((en_progreso / total_tratamientos) * 100, 1)
        porcentaje_pendiente = round((pendientes / total_tratamientos) * 100, 1)
        porcentaje_cancelado = round((cancelados / total_tratamientos) * 100, 1) if cancelados > 0 else 0
    else:
        porcentaje_completado = porcentaje_en_progreso = porcentaje_pendiente = porcentaje_cancelado = 0
    
    # ============ KPIs GENERALES ============
    total_ingresos_año = sum(ingresos_mensuales)
    total_pacientes_nuevos = sum(pacientes_nuevos_mes)
    total_pacientes_recurrentes = sum(pacientes_recurrentes_mes)
    
    # Lista de años disponibles para el selector
    años_disponibles = list(range(2020, now.year + 1))
    
    context = {
        # Filtros
        'año_seleccionado': año_seleccionado,
        'años_disponibles': años_disponibles,
        
        # KPIs
        'total_ingresos_año': total_ingresos_año,
        'total_pacientes_nuevos': total_pacientes_nuevos,
        'total_pacientes_recurrentes': total_pacientes_recurrentes,
        'total_tratamientos': total_tratamientos,
        
        # Gráfico 1: Ingresos Mensuales
        'ingresos_mensuales': ingresos_mensuales,
        'meses_labels': meses_labels,
        
        # Gráfico 2: Tratamientos Más Comunes
        'tratamientos_labels': tratamientos_labels,
        'tratamientos_data': tratamientos_data,
        
        # Gráfico 3: Pacientes Nuevos vs Recurrentes
        'pacientes_nuevos_mes': pacientes_nuevos_mes,
        'pacientes_recurrentes_mes': pacientes_recurrentes_mes,
        
        # Gráfico 4: Tasa de Completación
        'completados': completados,
        'en_progreso': en_progreso,
        'pendientes': pendientes,
        'cancelados': cancelados,
        'porcentaje_completado': porcentaje_completado,
        'porcentaje_en_progreso': porcentaje_en_progreso,
        'porcentaje_pendiente': porcentaje_pendiente,
        'porcentaje_cancelado': porcentaje_cancelado,
    }
    
    return render(request, 'dashboard/estadisticas.html', context)
