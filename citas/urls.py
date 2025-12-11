from django.urls import path
from . import views

urlpatterns = [
    path('calendario/', views.calendario_view, name='calendario'),
    path('eventos/', views.lista_eventos_view, name='lista_eventos'),
    path('api/eventos/', views.api_eventos_view, name='api_eventos'),
]
