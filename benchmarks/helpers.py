#!/usr/bin/env python3
"""
Funciones auxiliares para benchmarking
"""

import subprocess
import psutil
import time
import board
import busio
from adafruit_ina219 import INA219

def get_cpu_temp():
    """Obtener temperatura del CPU en Celsius"""
    try:
        temp = subprocess.check_output(
            "vcgencmd measure_temp", 
            shell=True
        ).decode()
        temp_value = float(temp.replace("temp=", "").replace("'C\n", ""))
        return temp_value
    except:
        return None

def get_memory_usage():
    """
    Medir uso de memoria a dos niveles:
    - Proceso: memoria específica del algoritmo
    - Sistema: impacto en el sistema completo
    """
    process_mem = psutil.Process().memory_info().rss / (1024**2)
    system_mem = psutil.virtual_memory().used / (1024**2)
    return {
        'process_mb': process_mem,
        'system_mb': system_mem
    }

def setup_ina219():
    """Configurar sensor INA219"""
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        ina = INA219(i2c, addr=0x40)
        return ina
    except Exception as e:
        print(f"⚠️Eror configurando INA219: {e}")
        return None

def get_ina219_reading(ina):
    """Obtener lectura de corriente del INA219"""
    if ina is None:
        return None
    try:
        return ina.current  # en mA
    except:
        return None

def wait_cooldown(seconds=2):
    """Esperar entre mediciones para evitar sobrecalentamiento"""
    time.sleep(seconds)
