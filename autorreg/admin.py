from django.contrib import admin
from .models import RegistroSesion

@admin.register(RegistroSesion)
class RegistroSesionAdmin(admin.ModelAdmin):
    # Columnas que veremos en la tabla resumen
    list_display = ('deportista', 'fecha', 'readiness', 'rpe')
    
    # Filtros laterales muy útiles para un entrenador
    list_filter = ('fecha', 'deportista')
    
    # Buscador por nombre de usuario
    search_fields = ('deportista__username',)