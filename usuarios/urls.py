# usuarios/urls.py
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Gestión de usuarios
    path('', views.lista_usuarios, name='lista'),
    path('crear/', views.crear_usuario, name='crear'),
    path('<int:user_id>/editar/', views.editar_usuario, name='editar'),
    path('<int:user_id>/toggle/', views.toggle_usuario, name='toggle'),
]
