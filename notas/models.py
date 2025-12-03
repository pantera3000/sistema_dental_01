# notas/models.py

from django.db import models
from django.urls import reverse
from pacientes.models import Paciente

class Nota(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='notas',
        null=True,
        blank=True,
        verbose_name="Paciente (opcional)"
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título"
    )
    contenido = models.TextField(
        verbose_name="Contenido"
    )
    creado_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    actualizado_en = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )

    class Meta:
        verbose_name = "Nota"
        verbose_name_plural = "Notas"
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.titulo} - {self.creado_en.strftime('%d/%m/%Y')}"

    def get_absolute_url(self):
        return reverse('notas:detalle', kwargs={'pk': self.pk})


class ImagenNota(models.Model):
    nota = models.ForeignKey(
        Nota,
        on_delete=models.CASCADE,
        related_name='imagenes',
        verbose_name="Nota"
    )
    imagen = models.ImageField(
        upload_to='notas/imagenes/',
        verbose_name="Imagen adjunta",
        blank=True,
        null=True
    )
    imagen_drive_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL de Google Drive",
        help_text="Pega aquí el link de compartir de Google Drive"
    )
    descripcion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Descripción (opcional)"
    )
    subido_en = models.DateTimeField(auto_now_add=True)
    
    def get_drive_embed_url(self):
        """Convierte URL de Drive a formato embebible"""
        if not self.imagen_drive_url:
            return None
        
        # Extraer FILE_ID de diferentes formatos de URL de Drive
        url = self.imagen_drive_url
        
        # Formato: https://drive.google.com/file/d/FILE_ID/view
        if '/file/d/' in url:
            file_id = url.split('/file/d/')[1].split('/')[0]
            return f"https://drive.google.com/uc?export=view&id={file_id}"
        
        # Formato: https://drive.google.com/open?id=FILE_ID
        if 'open?id=' in url:
            file_id = url.split('open?id=')[1].split('&')[0]
            return f"https://drive.google.com/uc?export=view&id={file_id}"
        
        # Si ya está en formato correcto o no se reconoce, devolver como está
        return url

    class Meta:
        verbose_name = "Imagen de Nota"
        verbose_name_plural = "Imágenes de Nota"

    def __str__(self):
        return f"Imagen para {self.nota.titulo}"