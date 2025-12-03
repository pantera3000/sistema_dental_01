from django.urls import path
from . import views

app_name = 'programa_salud'

urlpatterns = [
    path('paciente/<int:paciente_id>/programa/', views.crear_editar_programa, name='crear_editar_programa'),
    path('paciente/<int:paciente_id>/programa/pdf/', views.exportar_programa_pdf, name='exportar_pdf'),
]
