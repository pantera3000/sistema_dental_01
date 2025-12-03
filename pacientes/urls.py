# pacientes/urls.py

from django.urls import path
from . import views
from . import search_views
from . import views_ficha_medica

app_name = 'pacientes'

urlpatterns = [
    path('', views.ListaPacientesView.as_view(), name='lista'),
    path('nuevo/', views.CrearPacienteView.as_view(), name='crear'),
    path('<int:pk>/', views.DetallePacienteView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.EditarPacienteView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.EliminarPacienteView.as_view(), name='eliminar'),
    path('cumpleanos/', views.CumpleanosProximosView.as_view(), name='cumpleanos_proximos'),
    path('reportes/', views.reportes, name='reportes'),
    path('deudas/', views.pacientes_deudas, name='deudas'),
    # API de búsqueda global
    path('api/buscar/', search_views.busqueda_global, name='busqueda_global'),
    # Sistema de Ficha Médica Pública
    path('<int:paciente_id>/generar-ficha/', views_ficha_medica.generar_token_ficha, name='generar_ficha'),
]