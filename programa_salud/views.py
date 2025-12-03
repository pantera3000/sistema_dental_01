from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import ProgramaSalud
from .forms import ProgramaSaludForm
from pacientes.models import Paciente
from consultorio_dental.utils import render_to_pdf

def crear_editar_programa(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Intentar obtener programa existente
    try:
        programa = paciente.programa_salud
    except ProgramaSalud.DoesNotExist:
        programa = None

    if request.method == 'POST':
        if programa:
            form = ProgramaSaludForm(request.POST, instance=programa)
            mensaje_exito = "Programa de Salud actualizado correctamente."
        else:
            form = ProgramaSaludForm(request.POST)
            mensaje_exito = "Programa de Salud creado correctamente."

        if form.is_valid():
            programa = form.save(commit=False)
            programa.paciente = paciente
            programa.save()
            messages.success(request, mensaje_exito)
            return redirect('pacientes:detalle', pk=paciente_id)
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        if programa:
            form = ProgramaSaludForm(instance=programa)
        else:
            form = ProgramaSaludForm()

    return render(request, 'programa_salud/programa_form.html', {
        'form': form,
        'paciente': paciente,
        'programa': programa
    })

@login_required
def exportar_programa_pdf(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    programa = get_object_or_404(ProgramaSalud, paciente=paciente)
    
    context = {
        'paciente': paciente,
        'programa': programa,
    }
    
    pdf = render_to_pdf('programa_salud/programa_pdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Programa_Salud_{paciente.nombre_completo.replace(' ', '_')}.pdf"
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
    return HttpResponse("Error generando PDF", status=404)
