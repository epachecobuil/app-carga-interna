from django.db import models
from django.contrib.auth.models import User

class RegistroSesion(models.Model):
    deportista = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField()
    readiness = models.IntegerField()
    rpe = models.IntegerField()
    # Le ponemos default=60 para que no dé error con los registros guardados
    duracion_minutos = models.PositiveIntegerField(default=60) 
    # Permitimos que el usuario deje el campo de restingHR vacío, ya que no siempre se mide
    restingHR = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ['deportista', 'fecha']

    # NUEVO: El modelo calcula su propia carga automáticamente
    @property
    def carga_foster(self):
        return self.rpe * self.duracion_minutos

    def __str__(self):
        return f"{self.deportista.username} - {self.fecha}"