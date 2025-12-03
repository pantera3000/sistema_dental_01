from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import EvaluacionFuncional
from .forms import EvaluacionFuncionalForm
from pacientes.models import Paciente
from consultorio_dental.utils import render_to_pdf

def crear_editar_evaluacion(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Intentar obtener evaluación existente
    try:
        evaluacion = paciente.evaluacion_funcional
    except EvaluacionFuncional.DoesNotExist:
        evaluacion = None

    if request.method == 'POST':
        if evaluacion:
            form = EvaluacionFuncionalForm(request.POST, instance=evaluacion)
            mensaje_exito = "Evaluación actualizada correctamente."
        else:
            form = EvaluacionFuncionalForm(request.POST)
            mensaje_exito = "Evaluación creada correctamente."

        if form.is_valid():
            evaluacion = form.save(commit=False)
            evaluacion.paciente = paciente
            evaluacion.save()
            messages.success(request, mensaje_exito)
            return redirect('pacientes:detalle', pk=paciente_id)
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        if evaluacion:
            form = EvaluacionFuncionalForm(instance=evaluacion)
        else:
            form = EvaluacionFuncionalForm()

    return render(request, 'protocolo_ninos/evaluacion_form.html', {
        'form': form,
        'paciente': paciente,
        'evaluacion': evaluacion
    })

@login_required
def exportar_evaluacion_pdf(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    evaluacion = get_object_or_404(EvaluacionFuncional, paciente=paciente)
    
    context = {
        'paciente': paciente,
        'evaluacion': evaluacion,
    }
    
    pdf = render_to_pdf('protocolo_ninos/evaluacion_pdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Evaluacion_{paciente.nombre_completo.replace(' ', '_')}.pdf"
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
    return HttpResponse("Error generando PDF", status=404)
