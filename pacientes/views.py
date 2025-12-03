# pacientes/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import date, timedelta
from .models import Paciente
from .forms import PacienteForm
from tratamientos.models import Tratamiento, Pago
from protocolo_ninos.models import EvaluacionFuncional
from programa_salud.models import ProgramaSalud

from auditoria.utils import registrar_log

class ListaPacientesView(ListView):
    model = Paciente
    template_name = 'pacientes/lista_pacientes.html'
    context_object_name = 'pacientes'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Paciente.objects.filter(
                nombre_completo__icontains=query
            ) | Paciente.objects.filter(
                dni__icontains=query
            )
        return Paciente.objects.all()

class DetallePacienteView(DetailView):
    model = Paciente
    template_name = 'pacientes/detalle_paciente.html'
    context_object_name = 'paciente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente = self.object

        # Paginación para historias con conteo de imágenes (más reciente primero)
        historias = paciente.entradas_historia.annotate(num_imagenes=Count('imagenes')).order_by('-fecha')
        historias_paginator = Paginator(historias, 20)
        historias_page = self.request.GET.get('historias_page')
        context['historias_paginadas'] = historias_paginator.get_page(historias_page)

        # Paginación para tratamientos
        tratamientos = paciente.tratamientos.all()
        tratamientos_paginator = Paginator(tratamientos, 20)
        tratamientos_page = self.request.GET.get('tratamientos_page')
        context['tratamientos_paginados'] = tratamientos_paginator.get_page(tratamientos_page)

        # Paginación para notas con conteo de imágenes (más reciente primero)
        notas = paciente.notas.annotate(num_imagenes=Count('imagenes')).order_by('-creado_en')
        notas_paginator = Paginator(notas, 20)
        notas_page = self.request.GET.get('notas_page')
        context['notas_paginadas'] = notas_paginator.get_page(notas_page)

        # Obtener evaluación funcional si existe
        try:
            context['evaluacion_funcional'] = paciente.evaluacion_funcional
        except EvaluacionFuncional.DoesNotExist:
            context['evaluacion_funcional'] = None

        # Obtener programa salud si existe
        try:
            context['programa_salud'] = paciente.programa_salud
        except ProgramaSalud.DoesNotExist:
            context['programa_salud'] = None

        return context

class CrearPacienteView(CreateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'pacientes/crear_paciente.html'
    success_url = reverse_lazy('pacientes:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registrar en auditoría
        registrar_log(
            usuario=self.request.user,
            accion='CREAR',
            modelo='Paciente',
            objeto_id=self.object.id,
            objeto_repr=self.object.nombre_completo,
            detalles=f'Paciente creado: {self.object.nombre_completo} - DNI: {self.object.dni}',
            request=self.request
        )
        
        messages.success(self.request, "Paciente creado exitosamente.")
        return response

class EditarPacienteView(UpdateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'pacientes/editar_paciente.html'
    success_url = reverse_lazy('pacientes:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registrar en auditoría
        registrar_log(
            usuario=self.request.user,
            accion='EDITAR',
            modelo='Paciente',
            objeto_id=self.object.id,
            objeto_repr=self.object.nombre_completo,
            detalles=f'Paciente actualizado: {self.object.nombre_completo}',
            request=self.request
        )
        
        messages.success(self.request, "Paciente actualizado exitosamente.")
        return response

class EliminarPacienteView(DeleteView):
    model = Paciente
    template_name = 'pacientes/eliminar_paciente.html'
    success_url = reverse_lazy('pacientes:lista')

    def delete(self, request, *args, **kwargs):
        paciente = self.get_object()
        
        # Registrar en auditoría ANTES de eliminar
        registrar_log(
            usuario=request.user,
            accion='ELIMINAR',
            modelo='Paciente',
            objeto_id=paciente.id,
            objeto_repr=paciente.nombre_completo,
            detalles=f'Paciente eliminado: {paciente.nombre_completo} - DNI: {paciente.dni}',
            request=request
        )
        
        messages.success(request, "Paciente eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)

class CumpleanosProximosView(ListView):
    model = Paciente
    template_name = 'pacientes/cumpleanos_proximos.html'
    context_object_name = 'pacientes'
    paginate_by = 20

    def get_queryset(self):
        hoy = date.today()
        dias_a_mirar = 180  # Próximos 180 días
        pacientes = []

        for paciente in Paciente.objects.all():
            cumple = paciente.fecha_nacimiento.replace(year=hoy.year)
            if cumple < hoy:
                cumple = cumple.replace(year=hoy.year + 1)
            if (cumple - hoy).days <= dias_a_mirar:
                pacientes.append((paciente, (cumple - hoy).days))

        # Ordenar por días hasta el cumpleaños
        pacientes.sort(key=lambda x: x[1])
        return [p[0] for p in pacientes]

def reportes(request):
    """Vista para mostrar reportes generales del consultorio"""
    
    # === PACIENTES CON MAYOR DEUDA ===
    # Obtener todos los pacientes con tratamientos
    pacientes_con_deuda = []
    for paciente in Paciente.objects.all():
        tratamientos = paciente.tratamientos.all()
        if tratamientos.exists():
            deuda_total = sum(t.deuda for t in tratamientos)
            if deuda_total > 0:
                costo_total = sum(t.costo_total for t in tratamientos)
                porcentaje_deuda = (deuda_total / costo_total * 100) if costo_total > 0 else 0
                pacientes_con_deuda.append({
                    'paciente': paciente,
                    'deuda_total': deuda_total,
                    'costo_total': costo_total,
                    'porcentaje_deuda': round(porcentaje_deuda, 1)
                })
    
    # Ordenar por deuda descendente y tomar top 10
    pacientes_con_deuda.sort(key=lambda x: x['deuda_total'], reverse=True)
    top_deudores = pacientes_con_deuda[:10]
    
    # === PACIENTES CON MÁS TRATAMIENTOS ===
    pacientes_con_tratamientos = Paciente.objects.annotate(
        num_tratamientos=Count('tratamientos')
    ).filter(num_tratamientos__gt=0).order_by('-num_tratamientos')[:10]
    
    # === RESUMEN FINANCIERO ===
    # Total de ingresos (todos los pagos)
    try:
        total_ingresos = Pago.objects.aggregate(total=Sum('monto'))['total']
        if total_ingresos is None:
            total_ingresos = 0
    except Exception:
        total_ingresos = 0
    
    # Total de deudas pendientes
    total_deudas = sum(item['deuda_total'] for item in pacientes_con_deuda)
    
    # Pagos del mes actual (calendario)
    hoy = timezone.now()
    mes_actual = hoy.month
    anio_actual = hoy.year
    
    # Nombres de meses en español
    meses = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    nombre_mes = meses[mes_actual]
    
    try:
        pagos_mes = Pago.objects.filter(
            fecha_pago__year=anio_actual,
            fecha_pago__month=mes_actual
        ).aggregate(total=Sum('monto'))['total']
        
        if pagos_mes is None:
            pagos_mes = 0
    except Exception as e:
        print(f"Error calculando pagos del mes: {e}")
        pagos_mes = 0
    
    # Costo total de todos los tratamientos
    try:
        costo_total_tratamientos = Tratamiento.objects.aggregate(
            total=Sum('costo_total')
        )['total']
        if costo_total_tratamientos is None:
            costo_total_tratamientos = 0
    except Exception:
        costo_total_tratamientos = 0
    
    # === ESTADÍSTICAS DE TRATAMIENTOS ===
    # Contar tratamientos por estado
    stats_tratamientos = {
        'pendiente': Tratamiento.objects.filter(estado='pendiente').count(),
        'en_progreso': Tratamiento.objects.filter(estado='en_progreso').count(),
        'completado': Tratamiento.objects.filter(estado='completado').count(),
        'total': Tratamiento.objects.count()
    }
    
    context = {
        'top_deudores': top_deudores,
        'pacientes_con_tratamientos': pacientes_con_tratamientos,
        'total_ingresos': total_ingresos,
        'total_deudas': total_deudas,
        'pagos_mes': pagos_mes,
        'nombre_mes': nombre_mes,
        'costo_total_tratamientos': costo_total_tratamientos,
        'stats_tratamientos': stats_tratamientos,
    }
    
    return render(request, 'pacientes/reportes.html', context)

def pacientes_deudas(request):
    """Vista para mostrar todos los pacientes con deuda, con filtros por fecha"""
    
    # Obtener parámetros de filtro
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    filtro_rapido = request.GET.get('filtro_rapido', '')
    
    # Calcular fechas según filtro rápido
    hoy = timezone.now().date()
    if filtro_rapido == '1mes':
        fecha_desde = (hoy - timedelta(days=30)).strftime('%Y-%m-%d')
        fecha_hasta = hoy.strftime('%Y-%m-%d')
    elif filtro_rapido == '3meses':
        fecha_desde = (hoy - timedelta(days=90)).strftime('%Y-%m-%d')
        fecha_hasta = hoy.strftime('%Y-%m-%d')
    elif filtro_rapido == '6meses':
        fecha_desde = (hoy - timedelta(days=180)).strftime('%Y-%m-%d')
        fecha_hasta = hoy.strftime('%Y-%m-%d')
    elif filtro_rapido == 'anio':
        fecha_desde = f"{hoy.year}-01-01"
        fecha_hasta = hoy.strftime('%Y-%m-%d')
    
    # Obtener todos los pacientes con sus deudas
    pacientes_con_deuda = []
    
    for paciente in Paciente.objects.all():
        tratamientos = paciente.tratamientos.all()
        
        # Aplicar filtro de fecha si existe
        if fecha_desde and fecha_hasta:
            try:
                fecha_desde_obj = timezone.datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                fecha_hasta_obj = timezone.datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                tratamientos = tratamientos.filter(
                    fecha_inicio__gte=fecha_desde_obj,
                    fecha_inicio__lte=fecha_hasta_obj
                )
            except ValueError:
                pass  # Si hay error en las fechas, ignorar filtro
        
        if tratamientos.exists():
            deuda_total = sum(t.deuda for t in tratamientos)
            if deuda_total > 0:
                costo_total = sum(t.costo_total for t in tratamientos)
                porcentaje_deuda = (deuda_total / costo_total * 100) if costo_total > 0 else 0
                pacientes_con_deuda.append({
                    'paciente': paciente,
                    'deuda_total': deuda_total,
                    'costo_total': costo_total,
                    'porcentaje_deuda': round(porcentaje_deuda, 1)
                })
    
    # Ordenar por deuda descendente y tomar top 10
    pacientes_con_deuda.sort(key=lambda x: x['deuda_total'], reverse=True)
    top_deudores = pacientes_con_deuda[:10]
    
    # === PACIENTES CON MÁS TRATAMIENTOS ===
    pacientes_con_tratamientos = Paciente.objects.annotate(
        num_tratamientos=Count('tratamientos')
    ).filter(num_tratamientos__gt=0).order_by('-num_tratamientos')[:10]
    
    # === RESUMEN FINANCIERO ===
    # Total de ingresos (todos los pagos)
    try:
        total_ingresos = Pago.objects.aggregate(total=Sum('monto'))['total']
        if total_ingresos is None:
            total_ingresos = 0
    except Exception:
        total_ingresos = 0
    
    # Total de deudas pendientes
    total_deudas = sum(item['deuda_total'] for item in pacientes_con_deuda)
    
    # Pagos del mes actual (calendario)
    hoy = timezone.now()
    mes_actual = hoy.month
    anio_actual = hoy.year
    
    # Nombres de meses en español
    meses = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    nombre_mes = meses[mes_actual]
    
    try:
        pagos_mes = Pago.objects.filter(
            fecha_pago__year=anio_actual,
            fecha_pago__month=mes_actual
        ).aggregate(total=Sum('monto'))['total']
        
        if pagos_mes is None:
            pagos_mes = 0
    except Exception as e:
        print(f"Error calculando pagos del mes: {e}")
        pagos_mes = 0
    
    # Costo total de todos los tratamientos
    try:
        costo_total_tratamientos = Tratamiento.objects.aggregate(
            total=Sum('costo_total')
        )['total']
        if costo_total_tratamientos is None:
            costo_total_tratamientos = 0
    except Exception:
        costo_total_tratamientos = 0
    
    # === ESTADÍSTICAS DE TRATAMIENTOS ===
    # Contar tratamientos por estado
    stats_tratamientos = {
        'pendiente': Tratamiento.objects.filter(estado='pendiente').count(),
        'en_progreso': Tratamiento.objects.filter(estado='en_progreso').count(),
        'completado': Tratamiento.objects.filter(estado='completado').count(),
        'total': Tratamiento.objects.count()
    }
    
    context = {
        'top_deudores': top_deudores,
        'pacientes_con_tratamientos': pacientes_con_tratamientos,
        'total_ingresos': total_ingresos,
        'total_deudas': total_deudas,
        'pagos_mes': pagos_mes,
        'nombre_mes': nombre_mes,
        'costo_total_tratamientos': costo_total_tratamientos,
        'stats_tratamientos': stats_tratamientos,
    }
    
    return render(request, 'pacientes/reportes.html', context)

def pacientes_deudas(request):
    """Vista para mostrar todos los pacientes con deuda, con filtros por fecha"""
    
    # Obtener parámetros de filtro
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    filtro_rapido = request.GET.get('filtro_rapido', '')
    
    # Calcular fechas según filtro rápido
    hoy = timezone.now().date()
    if filtro_rapido == '1mes':
        fecha_desde = (hoy - timedelta(days=30)).strftime('%Y-%m-%d')
        fecha_hasta = hoy.strftime('%Y-%m-%d')
    elif filtro_rapido == '3meses':
        fecha_desde = (hoy - timedelta(days=90)).strftime('%Y-%m-%d')
        fecha_hasta = hoy.strftime('%Y-%m-%d')
    elif filtro_rapido == '6meses':
        fecha_desde = (hoy - timedelta(days=180)).strftime('%Y-%m-%d')
        fecha_hasta = hoy.strftime('%Y-%m-%d')
    elif filtro_rapido == 'anio':
        fecha_desde = f"{hoy.year}-01-01"
        fecha_hasta = hoy.strftime('%Y-%m-%d')
    
    # Obtener todos los pacientes con sus deudas
    pacientes_con_deuda = []
    
    for paciente in Paciente.objects.all():
        tratamientos = paciente.tratamientos.all()
        
        # Aplicar filtro de fecha si existe
        if fecha_desde and fecha_hasta:
            try:
                fecha_desde_obj = timezone.datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                fecha_hasta_obj = timezone.datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                tratamientos = tratamientos.filter(
                    fecha_inicio__gte=fecha_desde_obj,
                    fecha_inicio__lte=fecha_hasta_obj
                )
            except ValueError:
                pass  # Si hay error en las fechas, ignorar filtro
        
        if tratamientos.exists():
            deuda_total = sum(t.deuda for t in tratamientos)
            
            if deuda_total > 0:
                costo_total = sum(t.costo_total for t in tratamientos)
                porcentaje_deuda = (deuda_total / costo_total * 100) if costo_total > 0 else 0
                
                # Obtener último pago
                ultimo_pago = None
                pagos = Pago.objects.filter(tratamiento__paciente=paciente).order_by('-fecha_pago')
                if pagos.exists():
                    ultimo_pago = pagos.first().fecha_pago
                
                # Contar tratamientos con deuda
                tratamientos_con_deuda = sum(1 for t in tratamientos if t.deuda > 0)
                
                pacientes_con_deuda.append({
                    'paciente': paciente,
                    'deuda_total': deuda_total,
                    'costo_total': costo_total,
                    'porcentaje_deuda': round(porcentaje_deuda, 1),
                    'num_tratamientos': tratamientos_con_deuda,
                    'ultimo_pago': ultimo_pago,
                })
    
    # Ordenar por deuda descendente
    pacientes_con_deuda.sort(key=lambda x: x['deuda_total'], reverse=True)
    
    # Calcular estadísticas
    total_pacientes = len(pacientes_con_deuda)
    total_deudas = sum(item['deuda_total'] for item in pacientes_con_deuda)
    deuda_promedio = total_deudas / total_pacientes if total_pacientes > 0 else 0
    deuda_minima = min((item['deuda_total'] for item in pacientes_con_deuda), default=0)
    deuda_maxima = max((item['deuda_total'] for item in pacientes_con_deuda), default=0)
    
    # Paginación
    paginator = Paginator(pacientes_con_deuda, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'pacientes_con_deuda': page_obj.object_list,
        'total_pacientes': total_pacientes,
        'total_deudas': total_deudas,
        'deuda_promedio': deuda_promedio,
        'deuda_minima': deuda_minima,
        'deuda_maxima': deuda_maxima,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'filtro_rapido': filtro_rapido,
    }
    
    return render(request, 'pacientes/pacientes_deudas.html', context)
