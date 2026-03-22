"""
Módulo de debugging para la integración con Intervals.icu
Ayuda a identificar problemas en la recuperación de HRV
"""
import requests
from requests.auth import HTTPBasicAuth
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class IntervalsAPIDebugger:
    """Herramienta para debuggear la API de Intervals con logs detallados (Resting Heart Rate)"""
    
    def __init__(self, athlete_id, api_key):
        self.athlete_id = athlete_id
        self.api_key = api_key
        self.base_url = "https://intervals.icu/api/v1"
        
    def test_connection(self):
        """Test básico: ¿Podemos conectar a la API?"""
        print("=" * 60)
        print("TEST 1: Conectividad con Intervals.icu")
        print("=" * 60)
        
        try:
            url = f"{self.base_url}/athlete/{self.athlete_id}"
            print(f"URL: {url}")
            print(f"Auth User: API_KEY")
            print(f"Auth Password: {'*' * len(self.api_key)}")
            
            respuesta = requests.get(
                url, 
                auth=HTTPBasicAuth('API_KEY', self.api_key),
                timeout=5
            )
            
            print(f"Status Code: {respuesta.status_code}")
            print(f"Headers: {dict(respuesta.headers)}")
            print(f"Contenido (primeros 500 caracteres): {respuesta.text[:500]}")
            
            return respuesta.status_code == 200
            
        except Exception as e:
            print(f"❌ ERROR: {type(e).__name__}: {e}")
            return False
    
    def test_wellness_endpoint(self, fecha_str):
        """Test específico: ¿Devuelve datos wellness y restingHR para esta fecha?"""
        print("\n" + "=" * 60)
        print(f"TEST 2: Endpoint Wellness (buscando 'restingHR') para fecha {fecha_str}")
        print("=" * 60)
        
        try:
            url = f"{self.base_url}/athlete/{self.athlete_id}/wellness/{fecha_str}"
            print(f"URL Completa: {url}")
            
            respuesta = requests.get(
                url,
                auth=HTTPBasicAuth('API_KEY', self.api_key),
                timeout=5
            )
            
            print(f"Status Code: {respuesta.status_code}")
            print(f"Response Text: {respuesta.text}")
            
            if respuesta.status_code == 200:
                datos = respuesta.json()
                print(f"JSON parseado: {json.dumps(datos, indent=2)}")
                
                # Validaciones
                if 'restingHR' in datos:
                    rhr_value = datos['restingHR']
                    print(f"✓ Campo 'restingHR' encontrado: {rhr_value} bpm (tipo: {type(rhr_value).__name__})")
                    if rhr_value is None:
                        print("  ⚠️  ADVERTENCIA: restingHR es NULL")
                    elif rhr_value == 0:
                        print("  ⚠️  ADVERTENCIA: restingHR es 0")
                    return rhr_value
                else:
                    print("❌ Campo 'restingHR' NO encontrado en la respuesta")
                    print(f"   Campos disponibles: {list(datos.keys())}")
                    return None
            else:
                print(f"❌ Error HTTP {respuesta.status_code}")
                return None
                
        except json.JSONDecodeError as e:
            print(f"❌ ERROR parsing JSON: {e}")
            print(f"   Respuesta recibida: {respuesta.text}")
            return None
        except Exception as e:
            print(f"❌ ERROR: {type(e).__name__}: {e}")
            return None
    
    def test_all(self, fecha_str):
        """Ejecuta todos los tests de debugging"""
        print("\n" + "🔍 INICIANDO DEBUGGING DE INTERVALS.ICU (Resting Heart Rate) 🔍".center(60))
        
        # Test 1: Conexión general
        conexion_ok = self.test_connection()
        
        if conexion_ok:
            # Test 2: Endpoint específico
            rhr = self.test_wellness_endpoint(fecha_str)
            
            print("\n" + "=" * 60)
            print("RESUMEN")
            print("=" * 60)
            if rhr is not None and rhr != 0:
                print(f"✓ Éxito: Resting Heart Rate obtenido = {rhr} bpm")
            else:
                print("✗ Falló: No se puede obtener Resting Heart Rate")
        else:
            print("\n❌ No se pudo conectar. Verifica:")
            print("   - ATHLETE_ID correcto")
            print("   - API_KEY válida")
            print("   - Conexión a internet")


# Función de conveniencia para usar directamente
def debug_intervals_rhr(athlete_id, api_key, fecha_str):
    """
    Función rápida para debuggear Resting Heart Rate
    
    Uso:
        from autorreg.intervals_debug import debug_intervals_rhr
        debug_intervals_rhr('i435252', 'tu_api_key', '2026-03-22')
    """
    debugger = IntervalsAPIDebugger(athlete_id, api_key)
    debugger.test_all(fecha_str)
