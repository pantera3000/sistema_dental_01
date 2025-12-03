# notas/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.forms import inlineformset_factory
from django.db.models import Q, Count
from datetime import date
from django.urls import reverse

from pacientes.models import Paciente
from .models import Nota, ImagenNota
from .forms import NotaForm, ImagenNotaForm

from auditoria.utils import registrar_log

class ListaNotasView(ListView):
    model = Nota
    template_name = 'notas/lista_notas.html'
    context_object_name = 'notas'
    paginate_by = 10

    def get_queryset(self):
        paciente_id = self.kwargs.get('paciente_id')
        queryset = Nota.objects.select_related('paciente').all()
        
        if paciente_id:
            self.paciente = get_object_or_404(Paciente, pk=paciente_id)
            queryset = queryset.filter(paciente_id=paciente_id)
        else:
            self.paciente = None

        # Filtros
        q = self.request.GET.get('q')
        paciente_filtro = self.request.GET.get('paciente')
        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')

        if q:
            queryset = queryset.filter(
                Q(titulo__icontains=q) |
                Q(contenido__icontains=q)
            )
        
        if paciente_filtro and not paciente_id:
            queryset = queryset.filter(paciente__nombre_completo__icontains=paciente_filtro)
        
        if fecha_inicio:
            queryset = queryset.filter(creado_en__date__gte=fecha_inicio)
        
        if fecha_fin:
            queryset = queryset.filter(creado_en__date__lte=fecha_fin)

        # Anotar con el conteo de imágenes
        queryset = queryset.annotate(num_imagenes=Count('imagenes'))

        return queryset.order_by('-creado_en')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paciente'] = getattr(self, 'paciente', None)
        return context

class DetalleNotaView(DetailView):
    model = Nota
    template_name = 'notas/detalle_nota.html'
    context_object_name = 'nota'

class CrearNotaView(CreateView):
    model = Nota
    form_class = NotaForm
    template_name = 'notas/crear_nota.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        paciente_id = self.kwargs.get('paciente_id')
        if paciente_id:
            kwargs['paciente_id'] = paciente_id
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente_id = self.kwargs.get('paciente_id')
        if paciente_id:
            context['paciente'] = get_object_or_404(Paciente, pk=paciente_id)
        if self.request.POST:
            context['imagenes_formset'] = self.get_imagenes_formset(self.request.POST, self.request.FILES)
        else:
            context['imagenes_formset'] = self.get_imagenes_formset()
        return context

    def get_imagenes_formset(self, *args, **kwargs):
        ImagenesFormSet = inlineformset_factory(
            Nota,
            ImagenNota,
            form=ImagenNotaForm,
            extra=3,
            can_delete=False
        )
        return ImagenesFormSet(*args, **kwargs)

    def form_valid(self, form):
        context = self.get_context_data()
        imagenes_formset = context['imagenes_formset']
        paciente_id = self.kwargs.get('paciente_id')
        if paciente_id:
            form.instance.paciente_id = paciente_id
        self.object = form.save()


        

        # Registrar en auditoría
        registrar_log(
            usuario=self.request.user,
            accion='CREAR',
            modelo='Nota',
            objeto_id=self.object.id,
            objeto_repr=self.object.titulo,
            detalles=f'Nota creada: {self.object.titulo} (Paciente: {self.object.paciente.nombre_completo if self.object.paciente else "Sin paciente"})',
            request=self.request
        )

              
        if imagenes_formset.is_valid():
            # Procesar manualmente para manejar ambos tipos de imagen
            for form_img in imagenes_formset:
                if form_img.cleaned_data and not form_img.cleaned_data.get('DELETE', False):
                    imagen_local = form_img.cleaned_data.get('imagen')
                    imagen_drive_url = form_img.cleaned_data.get('imagen_drive_url')
                    descripcion = form_img.cleaned_data.get('descripcion', '')
                    
                    # Si tiene ambos, crear dos registros separados
                    if imagen_local and imagen_drive_url:
                        # Crear registro para imagen local
                        ImagenNota.objects.create(
                            nota=self.object,
                            imagen=imagen_local,
                            descripcion=f"{descripcion} (Local)" if descripcion else "Imagen local"
                        )
                        # Crear registro para Drive
                        ImagenNota.objects.create(
                            nota=self.object,
                            imagen_drive_url=imagen_drive_url,
                            descripcion=f"{descripcion} (Drive)" if descripcion else "Imagen de Drive"
                        )
                    # Si solo tiene imagen local
                    elif imagen_local:
                        ImagenNota.objects.create(
                            nota=self.object,
                            imagen=imagen_local,
                            descripcion=descripcion
                        )
                    # Si solo tiene Drive URL
                    elif imagen_drive_url:
                        ImagenNota.objects.create(
                            nota=self.object,
                            imagen_drive_url=imagen_drive_url,
                            descripcion=descripcion
                        )
        
        messages.success(self.request, "Nota creada exitosamente.")
        return super().form_valid(form)

    def get_success_url(self):
        paciente_id = self.kwargs.get('paciente_id')
        if paciente_id:
            return reverse_lazy('pacientes:detalle', kwargs={'pk': paciente_id}) + '?notas_page=1'
        return reverse_lazy('notas:lista')


class EditarNotaView(UpdateView):
    model = Nota
    form_class = NotaForm
    template_name = 'notas/editar_nota.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paciente'] = self.object.paciente
        if self.request.POST:
            context['imagenes_formset'] = self.get_imagenes_formset(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )
        else:
            context['imagenes_formset'] = self.get_imagenes_formset(instance=self.object)
        return context

    def get_imagenes_formset(self, *args, **kwargs):
        return inlineformset_factory(
            Nota,
            ImagenNota,
            form=ImagenNotaForm,
            extra=1,
            can_delete=True
        )(*args, **kwargs)

    def form_valid(self, form):
        context = self.get_context_data()
        imagenes_formset = context['imagenes_formset']
        
        if imagenes_formset.is_valid():
            self.object = form.save()


            # Registrar en auditoría
            registrar_log(
                usuario=self.request.user,
                accion='EDITAR',
                modelo='Nota',
                objeto_id=self.object.id,
                objeto_repr=self.object.titulo,
                detalles=f'Nota actualizada: {self.object.titulo}',
                request=self.request
)



            
            # Procesar manualmente para manejar ambos tipos de imagen
            for form_img in imagenes_formset:
                if form_img.cleaned_data:
                    # Si es un formulario existente y está marcado para eliminar
                    if form_img.cleaned_data.get('DELETE', False):
                        if form_img.instance.pk:
                            form_img.instance.delete()
                        continue
                    
                    # Si es un formulario existente, NO hacer nada (ya existe en BD)
                    # Solo procesamos formularios NUEVOS
                    if form_img.instance.pk:
                        continue
                    
                    # Solo procesar formularios nuevos
                    imagen_local = form_img.cleaned_data.get('imagen')
                    imagen_drive_url = form_img.cleaned_data.get('imagen_drive_url')
                    descripcion = form_img.cleaned_data.get('descripcion', '')
                    
                    # Si tiene datos, crear nuevos registros
                    if imagen_local or imagen_drive_url:
                        # Si tiene ambos, crear dos registros
                        if imagen_local and imagen_drive_url:
                            ImagenNota.objects.create(
                                nota=self.object,
                                imagen=imagen_local,
                                descripcion=f"{descripcion} (Local)" if descripcion else "Imagen local"
                            )
                            ImagenNota.objects.create(
                                nota=self.object,
                                imagen_drive_url=imagen_drive_url,
                                descripcion=f"{descripcion} (Drive)" if descripcion else "Imagen de Drive"
                            )
                        elif imagen_local:
                            ImagenNota.objects.create(
                                nota=self.object,
                                imagen=imagen_local,
                                descripcion=descripcion
                            )
                        elif imagen_drive_url:
                            ImagenNota.objects.create(
                                nota=self.object,
                                imagen_drive_url=imagen_drive_url,
                                descripcion=descripcion
                            )
            
            messages.success(self.request, "Nota actualizada exitosamente.")
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('notas:detalle', kwargs={'pk': self.object.pk})


class EliminarNotaView(DeleteView):
    model = Nota
    template_name = 'notas/eliminar_nota.html'

    def get_success_url(self):
        if self.object.paciente:
            return reverse('pacientes:detalle', kwargs={'pk': self.object.paciente.pk}) + '?notas_page=1'
        return reverse('notas:lista')

    def delete(self, request, *args, **kwargs):
        nota = self.get_object()
        
        # Registrar en auditoría ANTES de eliminar
        registrar_log(
            usuario=request.user,
            accion='ELIMINAR',
            modelo='Nota',
            objeto_id=nota.id,
            objeto_repr=nota.titulo,
            detalles=f'Nota eliminada: {nota.titulo} (Paciente: {nota.paciente.nombre_completo if nota.paciente else "Sin paciente"})',
            request=request
        )
        
        messages.success(request, "Nota eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)