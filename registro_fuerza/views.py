from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ejercicio, SesionFuerza
from .forms import EjercicioForm, SesionFuerzaForm
#Importamos el modelo de tu otra aplicación
from autorreg.models import RegistroSesion 
from django.db.models import F, FloatField, ExpressionWrapper
from datetime import date

@login_required(login_url='login')
def panel_fuerza(request):
    hoy = date.today()
    
# Buscamos si ya hay un registro de autorregulación HOY para mostrar los minutos actuales en la casilla
    registro_hoy = RegistroSesion.objects.filter(deportista=request.user, fecha=hoy).first()
    minutos_actuales = registro_hoy.duracion_minutos if registro_hoy else ""

    if request.method == 'POST':
        # 1. Si el usuario está creando un EJERCICIO NUEVO
        if 'guardar_ejercicio' in request.POST:
            form_ejercicio = EjercicioForm(request.POST)
            if form_ejercicio.is_valid():
                ejercicio = form_ejercicio.save(commit=False)
                ejercicio.usuario = request.user
                ejercicio.save()
                messages.success(request, 'Nuevo ejercicio añadido a tu catálogo.')
                return redirect('panel_fuerza')
                
        # 2. Si el usuario está registrando una SERIE (Ya sin los minutos cruzados)
        elif 'guardar_sesion' in request.POST:
            form_sesion = SesionFuerzaForm(request.POST)
            if form_sesion.is_valid():
                sesion = form_sesion.save(commit=False)
                sesion.usuario = request.user
                sesion.save()
                messages.success(request, 'Serie registrada con éxito.')
                return redirect('panel_fuerza')
                
        # 3. NUEVO: Si el usuario pulsa "FINALIZAR ENTRENAMIENTO"
        elif 'guardar_tiempo' in request.POST:
            minutos = request.POST.get('minutos_totales')
            if minutos and minutos.isdigit():
                # Hace la conexión cruzada con la app 'autorreg'
                registro_rpe, creado = RegistroSesion.objects.get_or_create(
                    deportista=request.user,
                    fecha=hoy, # Guarda el tiempo en la fecha de hoy
                    defaults={'readiness': 5, 'rpe': 5, 'duracion_minutos': minutos}
                )
                if not creado:
                    registro_rpe.duracion_minutos = minutos
                    registro_rpe.save()
                messages.success(request, 'Tiempo total de sesión guardado. ¡Buen entrenamiento!')
                return redirect('panel_fuerza')
    else:
        form_ejercicio = EjercicioForm()
        form_sesion = SesionFuerzaForm(initial={'fecha': hoy})

    # Nos aseguramos de que en el desplegable solo salgan SUS ejercicios
    form_sesion.fields['ejercicio'].queryset = Ejercicio.objects.filter(usuario=request.user)

    # Obtenemos las series que ha hecho hoy
    historial_hoy = SesionFuerza.objects.filter(usuario=request.user, fecha=hoy).order_by('-id')

    # --- CÁLCULO DEL RÉCORD PERSONAL (PR) ---
    for registro in historial_hoy:
        # Multiplicamos kilos * repeticiones a nivel de base de datos y sacamos el mejor
        series_historicas = SesionFuerza.objects.filter(
            usuario=request.user, 
            ejercicio=registro.ejercicio
        ).annotate(
            resultado=ExpressionWrapper(F('kilos') * F('repeticiones'), output_field=FloatField())
        ).order_by('-resultado')
        
        if series_historicas.exists():
            mejor = series_historicas.first()
            # Le "pegamos" el récord al objeto directamente para leerlo fácil en el HTML
            registro.record_personal = f"{mejor.kilos}kg x {mejor.repeticiones} reps"
        else:
            registro.record_personal = "Sin récord previo"
            
    contexto = {
        'form_ejercicio': form_ejercicio,
        'form_sesion': form_sesion,
        'historial_hoy': historial_hoy,
        'minutos_actuales': minutos_actuales
    }
    return render(request, 'registro_fuerza/panel.html', contexto)