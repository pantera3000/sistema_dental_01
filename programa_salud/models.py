from django.db import models
from pacientes.models import Paciente

class ProgramaSalud(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, related_name='programa_salud')
    
    # --- Datos del Paciente (Edad se calcula en el modelo Paciente) ---
    # Hábitos
    es_fumador = models.BooleanField(default=False, verbose_name="Fumador")
    es_bebedor = models.BooleanField(default=False, verbose_name="Bebedor")

    # --- Evaluación de Funciones ---
    # Masticación
    MASTICACION_CHOICES = [
        ('derecho', 'Derecho'),
        ('izquierdo', 'Izquierdo'),
    ]
    masticacion_lado = models.CharField(max_length=20, choices=MASTICACION_CHOICES, blank=True, null=True, verbose_name="Masticación")

    # Ventana nasal predominante
    VENTANA_NASAL_CHOICES = [
        ('derecha', 'Derecha'),
        ('izquierda', 'Izquierda'),
    ]
    ventana_nasal_predominante = models.CharField(max_length=20, choices=VENTANA_NASAL_CHOICES, blank=True, null=True, verbose_name="Ventana nasal predominante")

    # Síndrome Simpático Silencioso (SSS) - Checkboxes
    sss_respiracion_oral = models.BooleanField(default=False, verbose_name="Respiración oral / Boca seca")
    sss_calidad_sueno = models.BooleanField(default=False, verbose_name="Calidad del sueño / Ronquido / Apnea")
    sss_gingivitis = models.BooleanField(default=False, verbose_name="Gingivitis / Periodontal / Policaries")
    sss_faringitis = models.BooleanField(default=False, verbose_name="Faringitis crónica")
    sss_atm = models.BooleanField(default=False, verbose_name="Desorden ATM / CAT / Bruxismo")
    sss_reflujo = models.BooleanField(default=False, verbose_name="Reflujo / Hernia de hiato / Digestivos")
    sss_cefaleas = models.BooleanField(default=False, verbose_name="Cefaleas / Migrañas / Vértigos")
    sss_cervical = models.BooleanField(default=False, verbose_name="Dolor cervical / Dolores varios")
    sss_patologia_homolateral = models.BooleanField(default=False, verbose_name="Patología homolateral")
    sss_masticacion_unilateral = models.BooleanField(default=False, verbose_name="Masticación unilateral")
    sss_astenia = models.BooleanField(default=False, verbose_name="Astenia / Agotamiento")
    sss_ansiedad = models.BooleanField(default=False, verbose_name="Ansiedad / Depresión")
    sss_alergias = models.BooleanField(default=False, verbose_name="Alergias / Rinitis / Asma")
    sss_hipertension = models.BooleanField(default=False, verbose_name="Hipertensión / Riesgo cardiovascular")

    # --- Antecedentes ---
    otras_patologias = models.TextField(blank=True, verbose_name="Otras patologías")
    medicacion = models.TextField(blank=True, verbose_name="Medicación")
    intervenciones_previas = models.TextField(blank=True, verbose_name="Intervenciones previas")
    ejercicio_fisico_antecedentes = models.TextField(blank=True, verbose_name="Ejercicio físico (Antecedentes)")

    # --- Actividades Diarias del Programa ---
    
    # 1. Enjuagues con aceite de oliva
    enjuagues_manana = models.BooleanField(default=False, verbose_name="Enjuagues Mañana")
    enjuagues_tarde = models.BooleanField(default=False, verbose_name="Enjuagues Tarde")

    # 2. AcuaConfort (Instrucciones estáticas, no requiere campos de entrada específicos más allá de confirmar si se asigna, pero el usuario no pidió checkbox de asignación, solo mostrarlo. Asumiremos que es parte del programa estándar)

    # 3. PlacaConfort / DegluConfort
    placa_talla = models.CharField(max_length=50, blank=True, verbose_name="Talla Placa/Deglu")
    placa_uso_relajacion = models.BooleanField(default=False, verbose_name="Usar 3 ratos al día (relajación)")
    placa_uso_noche = models.BooleanField(default=False, verbose_name="Usar todas las noches (dormir)")

    # 4. NarizConfort
    nariz_talla = models.CharField(max_length=50, blank=True, verbose_name="Talla NarizConfort")
    nariz_uso_derecho = models.BooleanField(default=False, verbose_name="Uso Derecho")
    nariz_uso_izquierdo = models.BooleanField(default=False, verbose_name="Uso Izquierdo")
    nariz_uso_bilateral = models.BooleanField(default=False, verbose_name="Uso Bilateral")

    # 5. Hueso de aceituna (Instrucción)
    
    # 6. Vaselina o cacao (Instrucción)

    # 7. Alimentación
    alimentacion_lado_derecho = models.BooleanField(default=False, verbose_name="Masticar lado Derecho")
    alimentacion_lado_izquierdo = models.BooleanField(default=False, verbose_name="Masticar lado Izquierdo")

    # 8. Hábitos alimenticios
    habitos_fruta_entera = models.BooleanField(default=False, verbose_name="Comer fruta entera, a bocados")
    habitos_evitar_carbonatadas = models.BooleanField(default=False, verbose_name="Evitar bebidas carbonatadas")
    habitos_reducir_refinados = models.BooleanField(default=False, verbose_name="Reducir lácteos / Azúcar / Sal / Harinas")
    
    # Regla 3-2-1
    regla_no_comer_3h = models.BooleanField(default=False, verbose_name="No comer 3h antes de dormir")
    regla_no_beber_2h = models.BooleanField(default=False, verbose_name="No beber 2h antes")
    regla_no_pantallas_1h = models.BooleanField(default=False, verbose_name="No pantallas 1h antes")

    # 9. Ejercicio físico (Programa)
    ejercicio_caminata = models.BooleanField(default=False, verbose_name="Caminata diaria (1 hora)")
    ejercicio_caminata_huesito = models.BooleanField(default=False, verbose_name="Caminata con huesito en la boca")
    ejercicio_labios_pegados = models.BooleanField(default=False, verbose_name="Labios bien pegados durante caminata")
    ejercicio_pesas = models.BooleanField(default=False, verbose_name="Levantar pesas (ganar masa muscular)")

    # 10. Hábitos generales
    habitos_reducir_tabaco_alcohol = models.BooleanField(default=False, verbose_name="Reducir tabaco y alcohol")

    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Programa Salud - {self.paciente.nombre_completo}"

    class Meta:
        verbose_name = "Programa de Salud"
        verbose_name_plural = "Programas de Salud"
