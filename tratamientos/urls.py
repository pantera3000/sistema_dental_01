# tratamientos/urls.py

from django.urls import path
from . import views

app_name = 'tratamientos'

urlpatterns = [
    # Tratamientos
    path('', views.ListaTratamientosView.as_view(), name='lista'),
    path('paciente/<int:paciente_id>/', views.ListaTratamientosView.as_view(), name='lista_por_paciente'),
    path('nuevo/<int:paciente_id>/', views.CrearTratamientoView.as_view(), name='crear_tratamiento'),
    path('<int:pk>/', views.DetalleTratamientoView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.EditarTratamientoView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.EliminarTratamientoView.as_view(), name='eliminar'),
    path('<int:pk>/eliminar/', views.EliminarTratamientoView.as_view(), name='eliminar_tratamiento'),
    
    # Pagos
    path('<int:tratamiento_id>/pago/nuevo/', views.CrearPagoView.as_view(), name='crear_pago'),
    path('pago/<int:pk>/eliminar/', views.EliminarPagoView.as_view(), name='eliminar_pago'),
    path('pagos/', views.ListaPagosView.as_view(), name='lista_pagos'),
    
    # Odontograma
    path('paciente/<int:paciente_id>/odontograma/', views.odontograma_view, name='odontograma'),
    path('api/odontograma/<int:paciente_id>/', views.api_obtener_odontograma, name='api_odontograma'),
    path('api/odontograma/<int:paciente_id>/guardar/', views.api_guardar_estado_diente, name='api_guardar_odontograma'),
    path('api/odontograma/<int:paciente_id>/historial/', views.api_historial_odontograma, name='api_historial_odontograma'),
]