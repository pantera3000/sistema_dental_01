# consultorio_dental/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from pacientes import views_ficha_medica, views_registro_publico

urlpatterns = [
    path('admin/', admin.site.urls),
    # URLs públicas
    path('registro-paciente/', views_registro_publico.registro_paciente_publico, name='registro_paciente'),
    path('registro-paciente/completado/', views_registro_publico.registro_completado, name='registro_completado'),
    path('ficha/<str:token>/', views_ficha_medica.ficha_publica, name='ficha_publica'),
    path('ficha/completada/', views_ficha_medica.ficha_completada, name='ficha_completada'),
    # URLs protegidas
    path('', include('usuarios.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('pacientes/', include('pacientes.urls')),
    path('historias/', include('historias.urls')),
    path('tratamientos/', include('tratamientos.urls')),
    path('notas/', include('notas.urls')),
    path('citas/', include('citas.urls')),
    path('configuracion/', include('configuracion.urls')),
    path('auditoria/', include('auditoria.urls')),
    path('protocolo-ninos/', include('protocolo_ninos.urls')),
    path('programa-salud/', include('programa_salud.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)