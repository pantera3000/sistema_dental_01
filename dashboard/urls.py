# dashboard/urls.py

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='index'),
    path('estadisticas/', views.estadisticas_view, name='estadisticas'),
    path('api/citas-widget/', views.dashboard_citas_api, name='api_citas_widget'),
]
