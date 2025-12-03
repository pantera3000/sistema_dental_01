from django.db import models
from pacientes.models import Paciente

class EvaluacionFuncional(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, related_name='evaluacion_funcional')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # --- Ventana Nasal ---
    VENTANA_NASAL_OPCIONES = [
        ('derecha', 'Derecha'),
        ('izquierda', 'Izquierda'),
    ]
    ventana_nasal_mas_cerrada = models.CharField(max_length=20, choices=VENTANA_NASAL_OPCIONES, blank=True, null=True)
    ventana_nasal_respira_mejor = models.CharField(max_length=20, choices=VENTANA_NASAL_OPCIONES, blank=True, null=True)

    # --- Sellado Labial ---
    sellado_labial_reposo = models.BooleanField(default=False, verbose_name="En reposo")
    
    # --- Cara ---
    fascies_adenoidea = models.BooleanField(default=False, verbose_name="Fascies adenoidea (ojeras)")
    labios_cortados = models.BooleanField(default=False, verbose_name="Labios cortados")

    # --- Patrón de Crecimiento ---
    PATRON_CRECIMIENTO_CHOICES = [
        ('braqui', 'Braqui'),
        ('meso', 'Meso'),
        ('dolico', 'Dólico'),
    ]
    patron_crecimiento = models.CharField(max_length=20, choices=PATRON_CRECIMIENTO_CHOICES, blank=True, null=True)

    # --- Oclusión ---
    MALOCLUSION_CHOICES = [
        ('clase_i', 'Clase I'),
        ('clase_ii', 'Clase II'),
        ('clase_iii', 'Clase III'),
    ]
    maloclusion = models.CharField(max_length=20, choices=MALOCLUSION_CHOICES, blank=True, null=True)

    MORDIDA_CRUZADA_CHOICES = [
        ('anterior', 'Anterior'),
        ('derecha', 'Derecha'),
        ('izquierda', 'Izquierda'),
    ]
    mordida_cruzada = models.CharField(max_length=20, choices=MORDIDA_CRUZADA_CHOICES, blank=True, null=True)

    mordida_abierta = models.BooleanField(default=False, verbose_name="Mordida abierta")

    SOBREMORDIDA_CHOICES = [
        ('grado_i', 'Grado I'),
        ('grado_ii', 'Grado II'),
    ]
    sobremordida = models.CharField(max_length=20, choices=SOBREMORDIDA_CHOICES, blank=True, null=True)

    # --- Amígdalas ---
    AMIGDALAS_GRADO_CHOICES = [
        ('grado_i', 'Grado I'),
        ('grado_ii', 'Grado II'),
        ('grado_iii', 'Grado III'),
    ]
    amigdalas_grado = models.CharField(max_length=20, choices=AMIGDALAS_GRADO_CHOICES, blank=True, null=True)
    
    AMIGDALAS_INFLAMADA_CHOICES = [
        ('derecha', 'Derecha'),
        ('izquierda', 'Izquierda'),
    ]
    amigdalas_mas_inflamada = models.CharField(max_length=20, choices=AMIGDALAS_INFLAMADA_CHOICES, blank=True, null=True)

    # --- Capacidad Masticatoria ---
    masticador_derecho = models.BooleanField(default=False, verbose_name="Masticador Derecho")
    masticador_izquierdo = models.BooleanField(default=False, verbose_name="Masticador Izquierdo")
    
    prefiere_yogurt = models.BooleanField(default=False, verbose_name="Prefiere Yogurt")
    prefiere_manzana = models.BooleanField(default=False, verbose_name="Prefiere Manzana")
    prefiere_naranja = models.BooleanField(default=False, verbose_name="Prefiere Naranja")
    prefiere_zumo = models.BooleanField(default=False, verbose_name="Prefiere Zumo")

    corta_bocados = models.BooleanField(default=False, verbose_name="¿Corta a bocados?")
    
    TIEMPO_COMER_CHOICES = [
        ('menos_20', '< 20 min'),
        ('30_min', '30 min'),
        ('mas_30', '> 30 min'),
    ]
    tiempo_comer = models.CharField(max_length=20, choices=TIEMPO_COMER_CHOICES, blank=True, null=True)

    aguanta_5min_labios_sellados = models.BooleanField(default=False, verbose_name="¿Aguanta 5 min con labios sellados?")
    dia_mantiene_sellado = models.BooleanField(default=False, verbose_name="¿Durante el día mantiene el sellado labial?")
    durmiendo_mantiene_sellado = models.BooleanField(default=False, verbose_name="¿Durmiendo mantiene el sellado labial?")
    es_respirador_oral = models.BooleanField(default=False, verbose_name="¿Es respirador oral?")

    # --- Capacidad Respiratoria / Deglución ---
    deglucion_traga_normalidad = models.BooleanField(default=False, verbose_name="Traga con normalidad")
    deglucion_traga_dificultad = models.BooleanField(default=False, verbose_name="Traga con dificultad")
    deglucion_lengua_dientes = models.BooleanField(default=False, verbose_name="Mete la lengua entre los dientes")
    deglucion_lengua_marcas = models.BooleanField(default=False, verbose_name="Lengua con marcas en los bordes")

    LENGUA_BOCA_ABIERTA_CHOICES = [
        ('muy_suelta', 'Al sacar la lengua es capaz de alcanzar la nariz: Lengua muy suelta'),
        ('suelta', 'Con la boca abierta la lengua llega al paladar: Lengua suelta'),
        ('frenectomia_recomendable', 'Con la boca abierta a lengua se queda a mitad de camino: Frenectomía recomendable'),
        ('frenectomia_segura', 'Con la boca abierta la lengua apenas sobrepasa los incisivos inferiores: Frenectomía segura'),
    ]
    lengua_boca_abierta = models.CharField(max_length=50, choices=LENGUA_BOCA_ABIERTA_CHOICES, blank=True, null=True)

    # --- Alergias e Historial ---
    es_alergico = models.BooleanField(default=False, verbose_name="¿Es alérgico a algo?")
    alergico_a_que = models.CharField(max_length=255, blank=True, null=True, verbose_name="¿A qué?")

    FRECUENCIA_CHOICES = [
        ('ninguna', 'Ninguna'),
        ('una', 'Una'),
        ('dos', 'Dos'),
        ('tres', 'Tres'),
        ('mas_tres', 'Más de tres'),
    ]
    resfrios_ultimo_anio = models.CharField(max_length=20, choices=FRECUENCIA_CHOICES, blank=True, null=True, verbose_name="Resfríos último año")
    enfermedades_respiratorias = models.CharField(max_length=20, choices=FRECUENCIA_CHOICES, blank=True, null=True, verbose_name="Amigdalitis/rinitis/otitis/bronquitis")
    antibioticos_ultimo_anio = models.CharField(max_length=20, choices=FRECUENCIA_CHOICES, blank=True, null=True, verbose_name="Antibióticos último año")

    # --- Sueño y Respiración ---
    RESPIRACION_NOCTURNA_CHOICES = [
        ('boca_cerrada_sin_ruido', 'Boca cerrada, sin ruido'),
        ('boca_cerrada_ronca', 'Boca cerrada, ronca'),
        ('boca_abierta_ronca_babea', 'Boca abierta, ronca y babea'),
    ]
    respiracion_nocturna = models.CharField(max_length=50, choices=RESPIRACION_NOCTURNA_CHOICES, blank=True, null=True)

    MOVILIDAD_DORMIR_CHOICES = [
        ('tranquilo', 'Tranquilo'),
        ('agitado', 'Se mueve mucho o agitado'),
    ]
    movilidad_dormir = models.CharField(max_length=20, choices=MOVILIDAD_DORMIR_CHOICES, blank=True, null=True)

    BRUXISMO_CHOICES = [
        ('centrico', 'Céntrico'),
        ('excentrico', 'Excéntrico'),
    ]
    bruxismo = models.CharField(max_length=20, choices=BRUXISMO_CHOICES, blank=True, null=True)

    RECUPERACION_DESPERTAR_CHOICES = [
        ('descansado', 'Se levanta descansado'),
        ('cuesta', 'Le cuesta levantarse'),
    ]
    recuperacion_despertar = models.CharField(max_length=20, choices=RECUPERACION_DESPERTAR_CHOICES, blank=True, null=True)

    # --- Evaluación de Funciones ---
    EVALUACION_NIVEL_CHOICES = [
        ('normal', 'Normal'),
        ('mejorable', 'Mejorable'),
        ('muy_mejorable', 'Muy mejorable'),
    ]
    
    eval_masticacion = models.CharField(max_length=20, choices=EVALUACION_NIVEL_CHOICES, blank=True, null=True)
    
    EVALUACION_RESPIRACION_CHOICES = [
        ('normal', 'Normal (nasal)'),
        ('mejorable', 'Mejorable (mixta)'),
        ('muy_mejorable', 'Muy mejorable (oral)'),
    ]
    eval_respiracion = models.CharField(max_length=20, choices=EVALUACION_RESPIRACION_CHOICES, blank=True, null=True)
    
    eval_deglucion = models.CharField(max_length=20, choices=EVALUACION_NIVEL_CHOICES, blank=True, null=True)

    # --- Evaluación Neurovegetativa ---
    FONACION_CHOICES = [
        ('normal', 'Habla normal'),
        ('dificultad', 'Dificultad con algunas sílabas'),
    ]
    fonacion = models.CharField(max_length=20, choices=FONACION_CHOICES, blank=True, null=True)

    ACTIVIDAD_FISICA_CHOICES = [
        ('mucho', 'Mucho ejercicio diario'),
        ('esporadico', 'Esporádico'),
        ('no_hace', 'No hace ejercicio'),
    ]
    actividad_fisica = models.CharField(max_length=20, choices=ACTIVIDAD_FISICA_CHOICES, blank=True, null=True)

    HABITOS_ALIMENTARIOS_CHOICES = [
        ('sano', 'Come sano y a sus horas'),
        ('sano_snacks', 'Come sano + snacks'),
        ('procesado', 'Come mucho procesado y a deshora'),
    ]
    habitos_alimentarios = models.CharField(max_length=20, choices=HABITOS_ALIMENTARIOS_CHOICES, blank=True, null=True)

    PANTALLAS_CHOICES = [
        ('no_usa', 'No usa'),
        ('1h', '1h'),
        ('2h', '2h'),
        ('3h', '3h'),
    ]
    horas_pantallas = models.CharField(max_length=10, choices=PANTALLAS_CHOICES, blank=True, null=True)

    # --- Estado General ---
    estado_satisfactorio = models.BooleanField(default=False, verbose_name="Satisfactorio")
    estado_mejorable = models.BooleanField(default=False, verbose_name="Mejorable")
    estado_muy_mejorable = models.BooleanField(default=False, verbose_name="Muy mejorable")

    antecedentes_interes = models.TextField(blank=True, null=True, verbose_name="Antecedentes de interés")
    enfermedad_actual = models.TextField(blank=True, null=True, verbose_name="Enfermedad actual")
    medicacion_actual = models.TextField(blank=True, null=True, verbose_name="Medicación actual")

    # --- Plan de Tratamiento ---
    plan_refuerzo_habitos = models.BooleanField(default=False, verbose_name="Solo refuerzo de hábitos saludables")
    plan_placa_confort = models.BooleanField(default=False, verbose_name="PlacaConfort y recomendaciones")
    plan_deglu_confort = models.BooleanField(default=False, verbose_name="DegluConfort y recomendaciones")
    plan_nariz_confort = models.BooleanField(default=False, verbose_name="NarizConfort y recomendaciones")
    plan_mascalin = models.BooleanField(default=False, verbose_name="Mascalín (>5 años)")
    
    plan_retirada_lacteos = models.BooleanField(default=False, verbose_name="Retirada lácteos (1 mes)")
    plan_evitar_azucar = models.BooleanField(default=False, verbose_name="Evitar azúcar y harinas")
    plan_alimentos_duros = models.BooleanField(default=False, verbose_name="Alimentos duros/correosos")
    
    plan_comer_sin_cubiertos = models.BooleanField(default=False, verbose_name="Comer sin cubiertos")
    
    LADO_PREFERENTE_CHOICES = [
        ('derecho', 'Derecho'),
        ('izquierdo', 'Izquierdo'),
    ]
    plan_comer_lado_preferente = models.CharField(max_length=20, choices=LADO_PREFERENTE_CHOICES, blank=True, null=True)

    def __str__(self):
        return f"Evaluación Funcional de {self.paciente}"
