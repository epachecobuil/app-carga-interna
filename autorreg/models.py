from django.db import models
from django.contrib.auth.models import User

class RegistroSesion(models.Model):
    # Relacionamos el registro con el deportista (usuario de Django)
    deportista = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField()
    
    # Restringimos los valores del 1 al 10
    ESCALA_1_10 = [(i, str(i)) for i in range(1, 11)]
    
    readiness = models.IntegerField(choices=ESCALA_1_10, verbose_name="Readiness (Preparación)")
    rpe = models.IntegerField(choices=ESCALA_1_10, verbose_name="RPE (Esfuerzo Percibido)")

    class Meta:
        # Esto evita que un deportista cree dos registros distintos el mismo día
        unique_together = ('deportista', 'fecha')
        ordering = ['-fecha'] # Ordena los registros del más reciente al más antiguo

    def __str__(self):
        return f"{self.deportista.username} - {self.fecha} - RPE: {self.rpe}"