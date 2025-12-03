# configuracion/models.py
from django.db import models

class ConfiguracionConsultorio(models.Model):
    """Configuración global del consultorio para PDFs y documentos"""
    nombre_consultorio = models.CharField(
        max_length=200,
        default='Consultorio Dental',
        verbose_name="Nombre del Consultorio"
    )
    titulo_pdf = models.CharField(
        max_length=100,
        default='ODONTOGRAMA',
        verbose_name="Título del PDF"
    )
    logo = models.ImageField(
        upload_to='configuracion/logos/',
        null=True,
        blank=True,
        verbose_name="Logo del Consultorio"
    )
    direccion = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="Dirección"
    )
    telefono = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Teléfono"
    )
    email = models.EmailField(
        blank=True,
        verbose_name="Email"
    )
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración del Consultorio"
        verbose_name_plural = "Configuración del Consultorio"
    
    def __str__(self):
        return f"Configuración: {self.nombre_consultorio}"
    
    @classmethod
    def get_configuracion(cls):
        """Obtiene o crea la configuración única"""
        config, created = cls.objects.get_or_create(pk=1)
        return config
