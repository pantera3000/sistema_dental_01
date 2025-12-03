# pacientes/models.py

from django.db import models
from django.urls import reverse
from django.core.validators import MinLengthValidator
from datetime import date
import uuid
from datetime import timedelta
from django.utils import timezone


class Paciente(models.Model):
    # === DATOS PERSONALES ===
    nombre_completo = models.CharField(
        max_length=150,
        verbose_name="Nombre completo",
        help_text="Nombres y apellidos completos"
    )
    dni = models.CharField(
        max_length=8,
        unique=True,
        verbose_name="DNI",
        validators=[MinLengthValidator(8)],
        help_text="Documento Nacional de Identidad (8 dígitos)"
    )
    fecha_nacimiento = models.DateField(
        verbose_name="Fecha de nacimiento"
    )
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    genero = models.CharField(
        max_length=1,
        choices=GENERO_CHOICES,
        verbose_name="Género"
    )
    ESTADO_CIVIL_CHOICES = [
        ('S', 'Soltero/a'),
        ('C', 'Casado/a'),
        ('D', 'Divorciado/a'),
        ('V', 'Viudo/a'),
        ('U', 'Unión libre'),
    ]
    estado_civil = models.CharField(
        max_length=1,
        choices=ESTADO_CIVIL_CHOICES,
        verbose_name="Estado civil"
    )
    telefono = models.CharField(
        max_length=15,
        blank=True,
        verbose_name="Teléfono"
    )
    distrito = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Distrito"
    )
    direccion = models.TextField(
        blank=True,
        verbose_name="Dirección"
    )
    email = models.EmailField(
        blank=True,
        verbose_name="Email"
    )
    ocupacion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ocupación"
    )
    nombre_tutor = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nombre del tutor (si aplica)"
    )

    # === ANTECEDENTES MÉDICOS ===
    enfermedades_previas = models.TextField(
        blank=True,
        verbose_name="Enfermedades previas"
    )
    alergias = models.TextField(
        blank=True,
        verbose_name="Alergias"
    )
    GRUPO_SANGUINEO_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    grupo_sanguineo = models.CharField(
        max_length=3,
        choices=GRUPO_SANGUINEO_CHOICES,
        blank=True,
        verbose_name="Grupo sanguíneo"
    )

    # === HISTORIA DENTAL ===
    tratamientos_previos = models.TextField(
        blank=True,
        verbose_name="Tratamientos dentales previos"
    )
    experiencias_dentales = models.TextField(
        blank=True,
        verbose_name="Experiencias dentales (miedo, ansiedad, etc.)"
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones generales"
    )

    # === METADATOS ===
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    @property
    def dias_hasta_cumple(self):
        hoy = date.today()
        cumple = self.fecha_nacimiento.replace(year=hoy.year)
        if cumple < hoy:
            cumple = cumple.replace(year=hoy.year + 1)
        return (cumple - hoy).days

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['nombre_completo']

    def __str__(self):
        return f"{self.nombre_completo} (DNI: {self.dni})"

    def get_absolute_url(self):
        return reverse('pacientes:detalle', kwargs={'pk': self.pk})

    @property
    def edad(self):
        if self.fecha_nacimiento:
            today = date.today()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None




# ============================================
# SISTEMA DE FICHA MÉDICA PÚBLICA
# ============================================


class TokenFichaPaciente(models.Model):
    """Token único para acceso público al formulario de ficha médica"""
    
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='tokens_ficha',
        verbose_name="Paciente"
    )
    token = models.CharField(
        max_length=32,
        unique=True,
        verbose_name="Token único"
    )
    creado_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    expira_en = models.DateTimeField(
        verbose_name="Fecha de expiración"
    )
    completado = models.BooleanField(
        default=False,
        verbose_name="Completado"
    )
    completado_en = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de completado"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP"
    )
    
    class Meta:
        verbose_name = "Token de Ficha Médica"
        verbose_name_plural = "Tokens de Fichas Médicas"
        ordering = ['-creado_en']
    
    def __str__(self):
        return f"Token para {self.paciente.nombre_completo} - {'Completado' if self.completado else 'Pendiente'}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Solo al crear
            self.token = uuid.uuid4().hex
        if not self.expira_en:
            self.expira_en = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)
    
    @property
    def esta_vigente(self):
        """Verifica si el token está vigente"""
        return not self.completado and timezone.now() < self.expira_en
    
    @property
    def dias_restantes(self):
        """Calcula días restantes antes de expirar"""
        if self.completado:
            return 0
        delta = self.expira_en - timezone.now()
        return max(0, delta.days)


class FichaMedicaPaciente(models.Model):
    """Ficha médica completa del paciente llenada públicamente"""
    
    paciente = models.OneToOneField(
        Paciente,
        on_delete=models.CASCADE,
        related_name='ficha_medica',
        verbose_name="Paciente"
    )
    
    # === DATOS PERSONALES ADICIONALES ===
    email = models.EmailField(
        verbose_name="Correo electrónico"
    )
    direccion_completa = models.TextField(
        verbose_name="Dirección completa"
    )
    ocupacion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ocupación"
    )
    
    # === ANTECEDENTES MÉDICOS ===
    tiene_enfermedades = models.BooleanField(
        default=False,
        verbose_name="¿Padece alguna enfermedad?"
    )
    enfermedades_detalle = models.TextField(
        blank=True,
        verbose_name="Detalle de enfermedades"
    )
    
    toma_medicamentos = models.BooleanField(
        default=False,
        verbose_name="¿Toma medicamentos?"
    )
    medicamentos_detalle = models.TextField(
        blank=True,
        verbose_name="Detalle de medicamentos"
    )
    
    tiene_alergias = models.BooleanField(
        default=False,
        verbose_name="¿Tiene alergias?"
    )
    alergias_detalle = models.TextField(
        blank=True,
        verbose_name="Detalle de alergias"
    )
    
    esta_embarazada = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="¿Está embarazada? (solo mujeres)"
    )
    
    tiene_cirugias_previas = models.BooleanField(
        default=False,
        verbose_name="¿Ha tenido cirugías?"
    )
    cirugias_detalle = models.TextField(
        blank=True,
        verbose_name="Detalle de cirugías"
    )
    
    # === ANTECEDENTES DENTALES ===
    ultima_visita_dentista = models.DateField(
        null=True,
        blank=True,
        verbose_name="Última visita al dentista"
    )
    
    tiene_tratamientos_previos = models.BooleanField(
        default=False,
        verbose_name="¿Ha tenido tratamientos dentales?"
    )
    tratamientos_previos_detalle = models.TextField(
        blank=True,
        verbose_name="Detalle de tratamientos previos"
    )
    
    problemas_dentales_actuales = models.TextField(
        verbose_name="Problemas dentales actuales"
    )
    
    motivo_consulta = models.TextField(
        verbose_name="Motivo de la consulta"
    )
    
    # === CONSENTIMIENTOS ===
    acepta_tratamiento_datos = models.BooleanField(
        default=False,
        verbose_name="Acepta tratamiento de datos personales"
    )
    acepta_contacto = models.BooleanField(
        default=False,
        verbose_name="Acepta ser contactado por WhatsApp/Email"
    )
    
    # === METADATA ===
    fecha_completado = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de completado"
    )
    ip_completado = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP desde donde se completó"
    )
    
    class Meta:
        verbose_name = "Ficha Médica de Paciente"
        verbose_name_plural = "Fichas Médicas de Pacientes"
        ordering = ['-fecha_completado']
    
    def __str__(self):
        return f"Ficha médica de {self.paciente.nombre_completo}"