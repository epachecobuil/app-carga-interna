from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta # <-- NUEVO: Para sumar y restar días
import json
from .forms import RegistroSesionForm
from .models import RegistroSesion
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

@login_required(login_url='login') 
def panel_deportista(request):
    hoy = timezone.now().date()
    
    # 1. LÓGICA DE EDICIÓN HISTÓRICA
    # Miramos si la URL tiene un parámetro ?fecha=...
    fecha_str = request.GET.get('fecha')
    if fecha_str:
        try:
            fecha_activa = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            # Bloqueo de seguridad: No dejar editar más allá de 7 días
            if (hoy - fecha_activa).days > 7:
                messages.error(request, 'Por motivos de rigor científico, no se pueden editar sesiones de hace más de 7 días.')
                return redirect('panel')
        except ValueError:
            fecha_activa = hoy
    else:
        fecha_activa = hoy

    # 2. CARGAMOS EL REGISTRO (El de hoy, o el del día que seleccionó para editar)
    registro_activo = RegistroSesion.objects.filter(deportista=request.user, fecha=fecha_activa).first()

    if request.method == 'POST':
        formulario = RegistroSesionForm(request.POST, instance=registro_activo)
        if formulario.is_valid():
            registro = formulario.save(commit=False)
            registro.deportista = request.user
            registro.fecha = fecha_activa # Guardamos en la fecha correcta
            registro.save()
            messages.success(request, f'¡Métricas del {fecha_activa.strftime("%d/%m/%Y")} guardadas correctamente!')
            return redirect('panel') 
    else:
        formulario = RegistroSesionForm(instance=registro_activo)

    # 3. DATOS PARA LA GRÁFICA (Igual que antes)
    ultimos_registros = RegistroSesion.objects.filter(deportista=request.user).order_by('-fecha')[:10]
    registros_cronologicos = list(ultimos_registros)[::-1]
    
    fechas = [r.fecha.strftime("%d/%m") for r in registros_cronologicos]
    readiness_data = [r.readiness for r in registros_cronologicos]
    rpe_data = [r.rpe for r in registros_cronologicos]

    # 4. DATOS PARA LA TABLA DE HISTORIAL (Estrictamente últimos 7 días)
    limite_7_dias = hoy - timedelta(days=7)
    historial = RegistroSesion.objects.filter(
        deportista=request.user, 
        fecha__gte=limite_7_dias,
        fecha__lte=hoy
    ).order_by('-fecha')

    contexto = {
        'formulario': formulario,
        'fecha_activa': fecha_activa, # Lo pasamos al HTML para cambiar el título
        'hoy': hoy,
        'historial': historial,       # La lista de los últimos 7 días
        'fechas': json.dumps(fechas),
        'readiness_data': json.dumps(readiness_data),
        'rpe_data': json.dumps(rpe_data),
    }

    return render(request, 'autorreg/panel.html', contexto)


# ... (aquí sigue tu código del panel_deportista) ...

# AÑADE ESTA FUNCIÓN AL FINAL:
def registro_usuario(request):
    # Si el usuario ya está logueado, lo mandamos al panel
    if request.user.is_authenticated:
        return redirect('panel')

    if request.method == 'POST':
        formulario = UserCreationForm(request.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            # Logueamos al usuario automáticamente tras registrarse
            login(request, usuario)
            messages.success(request, f'¡Bienvenido a la plataforma, {usuario.username}!')
            return redirect('panel')
    else:
        formulario = UserCreationForm()

    return render(request, 'autorreg/registro.html', {'formulario': formulario})