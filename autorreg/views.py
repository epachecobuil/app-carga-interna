import requests
from requests.auth import HTTPBasicAuth
import json
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta #Para sumar y restar días
from .forms import RegistroSesionForm
from .models import RegistroSesion
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

logger = logging.getLogger(__name__)

def sincronizar_resting_heart_rate_intervals(usuario, fecha_cadena):
    """
    Se conecta a la API de Intervals.icu y devuelve el valor de Resting Heart Rate para una fecha dada (YYYY-MM-DD).
    
    Retorna:
        - float/int: Valor de restingHR si se obtiene correctamente
        - None: Si hay error en la conexión, autenticación, o el campo no existe
    """
    # Datos de autenticación (deberías guardarlos en variables de entorno en producción)
    ATHLETE_ID = 'i435252'
    API_KEY = '6bj09nd1vuontje38pwn3drd7'
    
    # La URL exacta para pedir los datos de "Wellness" (Salud) de un día concreto
    url = f"https://intervals.icu/api/v1/athlete/{ATHLETE_ID}/wellness/{fecha_cadena}"
    
    try:
        logger.debug(f"[HRV DEBUG] Conectando a: {url}")
        
        # Hacemos la llamada segura a la API. 
        # Nota técnica: Intervals obliga a usar la palabra exacta "API_KEY" como usuario.
        respuesta = requests.get(url, auth=HTTPBasicAuth('API_KEY', API_KEY), timeout=5)
        
        logger.debug(f"[HRV DEBUG] Status Code: {respuesta.status_code}")
        logger.debug(f"[HRV DEBUG] Response Headers: {dict(respuesta.headers)}")
        
        if respuesta.status_code == 200:
            try:
                datos = respuesta.json()
                logger.debug(f"[HRV DEBUG] JSON recibido: {datos}")
                
                # Buscamos el campo 'hrv' en el diccionario de respuesta
                if 'hrv' in datos:
                    hrv_valor = datos['restingHR']
                    logger.info(f"[HRV SUCCESS] HRV obtenido para {fecha_cadena}: {hrv_valor}")
                    return hrv_valor
                else:
                    logger.warning(f"[HRV WARNING] Campo 'hrv' no encontrado. Campos disponibles: {list(datos.keys())}")
                    return None
                    
            except json.JSONDecodeError as e:
                logger.error(f"[RHR ERROR] No se puede parsear JSON: {e}")
                logger.error(f"[RHR ERROR] Contenido recibido: {respuesta.text}")
                return None
        else:
            logger.error(f"[RHR ERROR] Status Code {respuesta.status_code} - {respuesta.text[:200]}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error("[RHR ERROR] Timeout: La API tardó más de 5 segundos en responder")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"[RHR ERROR] Error de conexión: {e}")
        return None
    except Exception as e:
        logger.error(f"[RHR ERROR] Excepción inesperada: {type(e).__name__}: {e}")
        return None

@login_required(login_url='login') 
def hub_principal(request):
    return render(request, 'autorreg/hub.html')

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
                return redirect('hub')
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
            #--- NUEVA INTEGRACIÓN CON INTERVALS ---
            # Pedimos el Resting Heart Rate de hoy (en formato 2026-03-22)
            fecha_api = fecha_activa.strftime('%Y-%m-%d')
            rhr_detectada = sincronizar_resting_heart_rate_intervals(request.user, fecha_api)
            if rhr_detectada is not None:  # no > 0
                registro.restingHR = rhr_detectada
            # ---------------------------------------
            registro.save()
            messages.success(request, f'¡Métricas del {fecha_activa.strftime("%d/%m/%Y")} guardadas correctamente!' if rhr_detectada else f'¡Métricas del {fecha_activa.strftime("%d/%m/%Y")} guardadas, pero no se pudo sincronizar el Resting Heart Rate!')
            return redirect('hub') 
    else:
        formulario = RegistroSesionForm(instance=registro_activo)

        # lógica: Recuperar Resting Heart Rate si no está establecido
        if registro_activo and registro_activo.restingHR is None:
            rhr_valor = sincronizar_resting_heart_rate_intervals(request.user, fecha_activa.strftime('%Y-%m-%d'))
            if rhr_valor is not None:
                registro_activo.restingHR = rhr_valor
                registro_activo.save()  # Guarda el valor en la base de datos


     # 3. DATOS PARA LA GRÁFICA Y EL HISTORIAL
    limite_7_dias = hoy - timedelta(days=7)
    limite_28_dias = hoy - timedelta(days=28) # Necesitamos 4 semanas para la crónica

    historial = RegistroSesion.objects.filter(
        deportista=request.user, 
        fecha__gte=limite_7_dias,
        fecha__lte=hoy
    ).order_by('-fecha')

    # --- NUEVA LÓGICA ACWR ---
    # A. Carga Aguda (Suma de los últimos 7 días)
    registros_agudos = RegistroSesion.objects.filter(deportista=request.user, fecha__gt=limite_7_dias, fecha__lte=hoy)
    carga_aguda = sum(r.carga_foster for r in registros_agudos)

    # B. Carga Crónica (Suma de los últimos 28 días / 4 semanas)
    registros_cronicos = RegistroSesion.objects.filter(deportista=request.user, fecha__gt=limite_28_dias, fecha__lte=hoy)
    carga_cronica_total = sum(r.carga_foster for r in registros_cronicos)
    carga_cronica = carga_cronica_total / 4 if carga_cronica_total > 0 else 0

    # C. Cálculo del ACWR
    acwr = round(carga_aguda / carga_cronica, 2) if carga_cronica > 0 else 0.00
    # -------------------------

    ultimos_registros = RegistroSesion.objects.filter(deportista=request.user).order_by('-fecha')[:10]
    registros_cronologicos = list(ultimos_registros)[::-1]
    
    fechas = [r.fecha.strftime("%d/%m") for r in registros_cronologicos]
    readiness_data = [r.readiness for r in registros_cronologicos]
    rpe_data = [r.rpe for r in registros_cronologicos]
    resting_hr_data = [r.restingHR for r in registros_cronologicos]

    # Añadimos nuestras nuevas variables matemáticas al contexto
    contexto = {
        'formulario': formulario,
        'fecha_activa': fecha_activa,
        'hoy': hoy,
        'historial': historial,
        'carga_aguda': carga_aguda,
        'carga_cronica': carga_cronica,
        'acwr': acwr,
        'fechas': json.dumps(fechas),
        'readiness_data': json.dumps(readiness_data),
        'rpe_data': json.dumps(rpe_data),
        'resting_hr_data': json.dumps(resting_hr_data),
        'registro': registro_activo, # Para mostrar la HRV en el panel si existe
    }

    return render(request, 'autorreg/panel.html', contexto)

def registro_usuario(request):
    # Si el usuario ya está logueado, lo mandamos al hub
    if request.user.is_authenticated:
        return redirect('hub')

    if request.method == 'POST':
        formulario = UserCreationForm(request.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            # Logueamos al usuario automáticamente tras registrarse
            login(request, usuario)
            messages.success(request, f'¡Bienvenido a la plataforma, {usuario.username}!')
            return redirect('hub')
    else:
        formulario = UserCreationForm()

    return render(request, 'autorreg/registro.html', {'formulario': formulario})