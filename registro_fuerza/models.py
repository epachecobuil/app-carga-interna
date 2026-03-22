from django.db import models
from django.contrib.auth.models import User

# 1. CATÁLOGO DE EJERCICIOS (Dinámico y personalizable)
class Ejercicio(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=150)
    enlace_video = models.URLField(blank=True, null=True, help_text="URL para visualizar la técnica")

    class Meta:
        # Evita crear dos veces el "Press Banca" por error
        unique_together = ['usuario', 'nombre'] 

    def __str__(self):
        return self.nombre

# 2. REGISTRO DIARIO DE FUERZA
class SesionFuerza(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField()
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    kilos = models.FloatField()
    series = models.IntegerField()
    repeticiones = models.IntegerField()

    def __str__(self):
        return f"{self.ejercicio.nombre} - {self.fecha}"