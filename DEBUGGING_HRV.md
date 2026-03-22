# 🔍 Guía de Debugging: Recuperación de HRV desde Intervals.icu

## 📋 Herramientas disponibles

Acabo de crear dos herramientas para tu proyecto:

1. **`autorreg/intervals_debug.py`** — Clase de debugging con logs detallados
2. **`debug_intervals.py`** — Script standalone para testear desde terminal

## 🚀 Cómo usar

### Opción 1: Script Standalone (RECOMENDADO - MÁS FÁCIL)

```bash
# Activa tu entorno virtual
cd c:\Users\enriq\OneDrive\Documentos\DevProjects\carga-interna-django-typescript
.\env_cint\Scripts\Activate.ps1

# Ejecuta el script de debugging
python debug_intervals.py
```

**Ingresa la fecha cuando te la pida (ej: 2026-03-22)**

El script te mostrará:
- ✓ Si puede conectarse a Intervals.icu
- ✓ Si la autenticación funciona
- ✓ Qué JSON devuelve exactamente
- ✓ Si el campo 'hrv' existe
- ✓ Cuál es el valor de HRV


### Opción 2: Django Shell (Si quieres más control)

```bash
# Activa tu entorno
.\env_cint\Scripts\Activate.ps1

# Entra en Django shell
python manage.py shell

# En el shell, copia esto:
from autorreg.intervals_debug import debug_intervals_hrv
from datetime import datetime

fecha = input("Fecha (YYYY-MM-DD): ")
debug_intervals_hrv('i435252', '6bj09nd1vuontje38pwn3drd7', fecha)

# Escribe: exit() para salir
```


## 🔧 Qué buscar en los resultados

### ✓ SI TODO VA BIEN:
```
TEST 1: Conectividad con Intervals.icu
Status Code: 200

TEST 2: Endpoint Wellness para fecha 2026-03-22
Status Code: 200
✓ Campo 'hrv' encontrado: 65.5 (tipo: float)
```

### ❌ SI FALLA - Posibles problemas:

#### **Error: Status Code 401 (Unauthorized)**
```
→ Problema: API_KEY o usuario incorrecto
→ Soluciones:
  1. Verifica tu API_KEY en la configuración de Intervals.icu
  2. Confirma que ATHLETE_ID sea correcto
  3. Revisa si tu cuenta de Intervals está activa
```

#### **Error: Status Code 403 (Forbidden)**
```
→ Problema: La API_KEY existe pero no tiene permisos
→ Soluciones:
  1. En Intervals.icu ve a Settings > API
  2. Regenera la clave API
  3. Asegúrate de que tenga permisos para "Wellness"
```

#### **Error: Status Code 404 (Not Found)**
```
→ Problema: La fecha o el endpoint no existen
→ Soluciones:
  1. Verifica que la fecha sea válida (YYYY-MM-DD)
  2. Verifica que ATHLETE_ID sea correcto
  3. Confirma que la fecha tiene datos en Intervals.icu
```

#### **Status 200 pero sin campo 'hrv'**
```
→ Problema: La API devuelve 200 pero no incluye HRV
→ Soluciones:
  1. Mira qué campos devuelve (el script muestra: "Campos disponibles: [...]")
  2. El nombre del campo podría ser diferente (ej: "RHR", "cardio", etc)
  3. Quizá esa fecha no tiene datos de HRV registrados en Intervals.icu
```

#### **Timeout: La API tardó más de 5 segundos**
```
→ Problema: Conexión lenta o API lenta
→ Soluciones:
  1. Verifica tu conexión a internet
  2. Intenta de nuevo (podría ser un pico temporal)
  3. Aumenta el timeout en views.py (timeout=10)
```

#### **ConnectionError**
```
→ Problema: No se puede conectar a Intervals.icu
→ Soluciones:
  1. Verifica tu conexión a internet
  2. Prueba: ping intervals.icu
  3. Si estás detrás de un proxy, configúralo en requests
```


## 📊 Interpretación de resultados

### Si el HRV es NULL:
```json
"hrv": null
```
→ Intervals.icu no tiene datos HRV para esa fecha (el deportista no lo registró)

### Si el HRV es 0:
```json
"hrv": 0
```
→ El deportista registró HRV = 0 (probablemente un dato incorrecto)

### Si el HRV es un número normal:
```json
"hrv": 65.5
```
→ ✓ Todo bien, HRV detectada correctamente


## 🛠️ Alternativas si Intervals.icu no devuelve el campo

Si después de todo esto la API simplemente **no devuelve HRV**, busca:

1. **¿Hay otro endpoint?**
   - Prueba: `GET /athlete/{id}/wellness/{date}/hrv` (versión específica)
   - Prueba: `GET /athlete/{id}/cardiac` (si HRV está en otra sección)

2. **¿El campo tiene otro nombre?**
   - Busca en la respuesta: `"rhr"`, `"heart_rate_variability"`, `"hrv_ms"`, etc.

3. **Panel manual de Intervals.icu**
   - Accede a https://intervals.icu
   - Ve a Wellness > esa fecha
   - ¿Está el HRV visible? Si no, no está registrado.


## 📝 Logs en Django

Para ver los logs en tiempo real (cuando uses la app):

1. Abre `carga_interna/settings.py`
2. Busca `LOGGING = {` 
3. Si no existe, agregalo (al final del archivo):

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'autorreg': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

Luego cuando ejecutes `python manage.py runserver` verás todos los `[HRV DEBUG]`, `[HRV ERROR]`, etc.


## 🎯 Resumen de acciones

```
┌─────────────────────────────────────────┐
│ 1. EJECUTA: python debug_intervals.py   │
├─────────────────────────────────────────┤
│ 2. ANALIZA EL STATUS CODE               │
│    - 200? → Mira si tiene 'hrv'         │
│    - 401? → API_KEY inválida            │
│    - 403? → Sin permisos                │
│    - 404? → ATHLETE_ID incorrecto       │
├─────────────────────────────────────────┤
│ 3. SI VES EL JSON COMPLETO              │
│    → Busca el campo correcto            │
│    → Cópialo y actualiza views.py       │
├─────────────────────────────────────────┤
│ 4. SI NO VES EL CAMPO                   │
│    → El deportista no ha registrado HRV │
│    → O no existe para esa fecha         │
└─────────────────────────────────────────┘
```

---

**¿Necesitas ayuda después de correr el script? Comparte el output aquí y te diré exactamente qué está mal.**
