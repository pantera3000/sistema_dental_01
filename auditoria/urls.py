# auditoria/urls.py
from django.urls import path
from . import views

app_name = 'auditoria'

urlpatterns = [
    path('logs/', views.logs_sistema, name='logs_sistema'),
]
