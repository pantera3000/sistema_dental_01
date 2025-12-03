from django.urls import path
from . import views

app_name = 'protocolo_ninos'

urlpatterns = [
    path('paciente/<int:paciente_id>/evaluacion/', views.crear_editar_evaluacion, name='crear_editar_evaluacion'),
    path('paciente/<int:paciente_id>/evaluacion/pdf/', views.exportar_evaluacion_pdf, name='exportar_pdf'),
]
