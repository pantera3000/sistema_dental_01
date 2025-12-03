# tratamientos/views.py
from datetime import date
import calendar 
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from pacientes.models import Paciente
from .models import Tratamiento, Pago, EstadoDiente, HistorialOdontograma
from .forms import TratamientoForm, PagoForm
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from auditoria.utils import registrar_log

# ===== TRATAMIENTOS =====

class ListaTratamientosView(ListView):
    model = Tratamiento
    template_name = 'tratamientos/lista_tratamientos.html'
    context_object_name = 'tratamientos'
    paginate_by = 20

    def get_queryset(self):
        paciente_id = self.kwargs.get('paciente_id')
        queryset = Tratamiento.objects.all()
        
        if paciente_id:
            self.paciente = get_object_or_404(Paciente, pk=paciente_id)
            queryset = queryset.filter(paciente_id=paciente_id)
        else:
            self.paciente = None

        # Filtros
        q = self.request.GET.get('q')
        estado = self.request.GET.get('estado')
        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')

        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q) |
                Q(paciente__nombre_completo__icontains=q)
            )
        
        if estado:
            queryset = queryset.filter(estado=estado)
        
        if fecha_inicio:
            queryset = queryset.filter(fecha_inicio__gte=fecha_inicio)
        
        if fecha_fin:
            queryset = queryset.filter(fecha_inicio__lte=fecha_fin)

        return queryset.order_by('-fecha_inicio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paciente'] = getattr(self, 'paciente', None)
        
        hoy = date.today()
        context['today'] = hoy
        
        # Fechas en formato ISO string (YYYY-MM-DD)
        context['this_year_start'] = hoy.replace(month=1, day=1).strftime('%Y-%m-%d')
        context['last_year_start'] = hoy.replace(year=hoy.year - 1, month=1, day=1).strftime('%Y-%m-%d')
        context['last_year_end'] = hoy.replace(year=hoy.year - 1, month=12, day=31).strftime('%Y-%m-%d')
        
        # Mes pasado
        if hoy.month == 1:
            last_month = 12
            last_year = hoy.year - 1
        else:
            last_month = hoy.month - 1
            last_year = hoy.year
        last_month_start = date(last_year, last_month, 1)
        last_month_end = date(last_year, last_month, calendar.monthrange(last_year, last_month)[1])
        context['last_month_start'] = last_month_start.strftime('%Y-%m-%d')
        context['last_month_end'] = last_month_end.strftime('%Y-%m-%d')
        
        # Este mes
        context['this_month_start'] = hoy.replace(day=1).strftime('%Y-%m-%d')
        context['this_month_end'] = hoy.strftime('%Y-%m-%d')
        
        return context

class DetalleTratamientoView(DetailView):
    model = Tratamiento
    template_name = 'tratamientos/detalle_tratamiento.html'
    context_object_name = 'tratamiento'

class CrearTratamientoView(CreateView):
    model = Tratamiento
    form_class = TratamientoForm
    template_name = 'tratamientos/crear_tratamiento.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paciente'] = get_object_or_404(Paciente, pk=self.kwargs['paciente_id'])
        return context

    def form_valid(self, form):
        paciente = get_object_or_404(Paciente, pk=self.kwargs['paciente_id'])
        form.instance.paciente = paciente
        response = super().form_valid(form)
        
        # Registrar en auditoría
        registrar_log(
            usuario=self.request.user,
            accion='CREAR',
            modelo='Tratamiento',
            objeto_id=self.object.id,
            objeto_repr=str(self.object),
            detalles=f'Tratamiento creado para {paciente.nombre_completo}: {self.object.descripcion}',
            request=self.request
        )
        
        messages.success(self.request, "Tratamiento creado exitosamente.")
        return response

    def get_success_url(self):
        paciente_id = self.kwargs.get('paciente_id')
        if paciente_id:
            return reverse_lazy('pacientes:detalle', kwargs={'pk': paciente_id}) + '?tratamientos_page=1'
        return reverse_lazy('tratamientos:lista')

class EliminarTratamientoView(DeleteView):
    model = Tratamiento
    template_name = 'tratamientos/eliminar_tratamiento.html'

    def get_success_url(self):
        referer = self.request.META.get('HTTP_REFERER', '')
        if 'pacientes' in referer:
            return reverse('pacientes:detalle', kwargs={'pk': self.object.paciente.pk})
        else:
            return reverse('tratamientos:lista')

    def delete(self, request, *args, **kwargs):
        tratamiento = self.get_object()
        if tratamiento.pagos.exists():
            messages.error(request, "No se puede eliminar un tratamiento con pagos asociados.")
            return redirect('tratamientos:detalle', pk=tratamiento.pk)
        
        # Registrar en auditoría antes de eliminar
        registrar_log(
            usuario=request.user,
            accion='ELIMINAR',
            modelo='Tratamiento',
            objeto_id=tratamiento.id,
            objeto_repr=str(tratamiento),
            detalles=f'Tratamiento eliminado: {tratamiento.descripcion} (Paciente: {tratamiento.paciente.nombre_completo})',
            request=request
        )
        
        messages.success(request, "Tratamiento eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)

class EditarTratamientoView(UpdateView):
    model = Tratamiento
    form_class = TratamientoForm
    template_name = 'tratamientos/editar_tratamiento.html'

    def get_success_url(self):
        return reverse('tratamientos:detalle', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        # Guardar estado anterior para auditoría
        tratamiento_anterior = Tratamiento.objects.get(pk=self.object.pk)
        estado_anterior = tratamiento_anterior.estado
        
        tratamiento = form.save(commit=False)
        if tratamiento.fecha_fin:
            tratamiento.estado = 'completado'
        else:
            if tratamiento.estado == 'completado':
                tratamiento.estado = 'en_progreso'
        tratamiento.save()
        
        # Registrar en auditoría
        cambios = {}
        if estado_anterior != tratamiento.estado:
            cambios['estado'] = {'antes': estado_anterior, 'después': tratamiento.estado}
        
        registrar_log(
            usuario=self.request.user,
            accion='EDITAR',
            modelo='Tratamiento',
            objeto_id=tratamiento.id,
            objeto_repr=str(tratamiento),
            cambios=cambios if cambios else None,
            detalles=f'Tratamiento actualizado: {tratamiento.descripcion}',
            request=self.request
        )
        
        messages.success(self.request, "Tratamiento actualizado exitosamente.")
        return super().form_valid(form)

# ===== PAGOS =====

class CrearPagoView(CreateView):
    model = Pago
    form_class = PagoForm
    template_name = 'tratamientos/crear_pago.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tratamiento'] = get_object_or_404(Tratamiento, pk=self.kwargs['tratamiento_id'])
        return context

    def form_valid(self, form):
        tratamiento = get_object_or_404(Tratamiento, pk=self.kwargs['tratamiento_id'])
        form.instance.tratamiento = tratamiento
        response = super().form_valid(form)
        
        # Registrar en auditoría
        registrar_log(
            usuario=self.request.user,
            accion='CREAR',
            modelo='Pago',
            objeto_id=self.object.id,
            objeto_repr=f'Pago S/. {self.object.monto}',
            detalles=f'Pago registrado: S/. {self.object.monto} - {self.object.get_metodo_pago_display()} (Tratamiento: {tratamiento.descripcion})',
            request=self.request
        )
        
        messages.success(self.request, "Pago registrado exitosamente.")
        return response

    def get_success_url(self):
        return reverse('tratamientos:detalle', kwargs={'pk': self.kwargs['tratamiento_id']})

class EliminarPagoView(DeleteView):
    model = Pago
    template_name = 'tratamientos/eliminar_pago.html'

    def get_success_url(self):
        return reverse('tratamientos:detalle', kwargs={'pk': self.object.tratamiento.pk})

    def delete(self, request, *args, **kwargs):
        pago = self.get_object()
        
        # Registrar en auditoría antes de eliminar
        registrar_log(
            usuario=request.user,
            accion='ELIMINAR',
            modelo='Pago',
            objeto_id=pago.id,
            objeto_repr=f'Pago S/. {pago.monto}',
            detalles=f'Pago eliminado: S/. {pago.monto} - {pago.get_metodo_pago_display()} (Tratamiento: {pago.tratamiento.descripcion})',
            request=request
        )
        
        messages.success(request, "Pago eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)

class ListaPagosView(ListView):
    model = Pago
    template_name = 'tratamientos/lista_pagos.html'
    context_object_name = 'pagos'
    paginate_by = 20

    def get_queryset(self):
        queryset = Pago.objects.select_related('tratamiento__paciente', 'tratamiento').all()
        
        q = self.request.GET.get('q')
        metodo = self.request.GET.get('metodo')
        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')
        paciente_id = self.request.GET.get('paciente_id')

        if q:
            queryset = queryset.filter(
                Q(tratamiento__paciente__nombre_completo__icontains=q) |
                Q(tratamiento__nombre__icontains=q) |
                Q(nota__icontains=q)
            )
        
        if metodo:
            queryset = queryset.filter(metodo_pago=metodo)
        
        if fecha_inicio:
            queryset = queryset.filter(fecha_pago__gte=fecha_inicio)
        
        if fecha_fin:
            queryset = queryset.filter(fecha_pago__lte=fecha_fin)
        
        if paciente_id:
            queryset = queryset.filter(tratamiento__paciente_id=paciente_id)

        return queryset.order_by('-fecha_pago')

# ===== ODONTOGRAMA =====

def odontograma_view(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    from configuracion.models import ConfiguracionConsultorio
    config = ConfiguracionConsultorio.get_configuracion()
    return render(request, 'tratamientos/odontograma.html', {
        'paciente': paciente,
        'config': config
    })

def api_obtener_odontograma(request, paciente_id):
    estados = EstadoDiente.objects.filter(paciente_id=paciente_id)
    data = []
    for estado in estados:
        data.append({
            'diente': estado.diente,
            'cara': estado.cara,
            'estado': estado.estado,
            'tratamiento_id': estado.tratamiento_id,
            'observaciones': estado.observaciones
        })
    return JsonResponse({'estados': data})

@require_POST
def api_guardar_estado_diente(request, paciente_id):
    try:
        data = json.loads(request.body)
        diente = data.get('diente')
        cara = data.get('cara')
        estado_valor = data.get('estado')
        observaciones = data.get('observaciones', '')
        
        if not all([diente, cara, estado_valor]):
            return JsonResponse({'error': 'Datos incompletos'}, status=400)

        estado_diente, created = EstadoDiente.objects.update_or_create(
            paciente_id=paciente_id,
            diente=diente,
            cara=cara,
            defaults={
                'estado': estado_valor,
                'observaciones': observaciones
            }
        )
        
        HistorialOdontograma.objects.create(
            paciente_id=paciente_id,
            diente=diente,
            cara=cara,
            estado=estado_valor,
            observaciones=observaciones
        )
        
        return JsonResponse({'status': 'success', 'message': 'Estado guardado'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def api_historial_odontograma(request, paciente_id):
    historial = HistorialOdontograma.objects.filter(paciente_id=paciente_id).order_by('-fecha_cambio')[:50]
    
    data = []
    for entry in historial:
        data.append({
            'diente': entry.diente,
            'cara': entry.cara,
            'estado': entry.estado,
            'observaciones': entry.observaciones,
            'fecha': entry.fecha_cambio.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return JsonResponse({'historial': data})