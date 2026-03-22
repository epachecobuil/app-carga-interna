#!/usr/bin/env python
"""
Script standalone para debuggear Intervals.icu
Ejecutar: python manage.py shell < debug_intervals_script.py
O desde terminal: python debug_intervals.py
"""
import os
import sys
from datetime import datetime, timedelta

# Importar las variables de tu settings si quieres, o pasar directamente
ATHLETE_ID = 'i435252'
API_KEY = '6bj09nd1vuontje38pwn3drd7'

# Agregar la ruta del proyecto si es necesario
sys.path.insert(0, os.path.dirname(__file__))

from autorreg.intervals_debug import debug_intervals_rhr

if __name__ == '__main__':
    print("\n🔧 HERRAMIENTA DE DEBUGGING PARA INTERVALS.ICU (Resting Heart Rate)\n")
    
    # Testear con hoy
    hoy = datetime.now().date()
    fecha_prueba = input(f"Ingresa la fecha para testear (YYYY-MM-DD) [default: {hoy}]: ").strip()
    
    if not fecha_prueba:
        fecha_prueba = hoy.strftime('%Y-%m-%d')
    
    print(f"\n📅 Testeando con fecha: {fecha_prueba}\n")
    
    debug_intervals_rhr(ATHLETE_ID, API_KEY, fecha_prueba)
    
    print("\n" + "=" * 60)
    print("SIGUIENTES PASOS SI FALLÓ:")
    print("=" * 60)
    print("1. Verifica que ATHLETE_ID sea correcto en Intervals.icu")
    print("2. Verifica que API_KEY sea válida y activa")
    print("3. Confirma que el formato de fecha sea YYYY-MM-DD")
    print("4. Mira si el endpoint regresa errores HTTP (401, 403, 404)")
    print("5. Chequea si el JSON tiene otros campos además de 'restingHR'")
