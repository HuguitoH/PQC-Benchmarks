#!/usr/bin/env python3
"""
Test del sensor INA219
"""

import board
import busio
from adafruit_ina219 import INA219
import time

# Crear bus I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Crear objeto INA219
ina = INA219(i2c, addr=0x40)

print("🔬 Probando sensor INA219...")
print("=" * 50)

for i in range(5):
    bus_voltage = ina.bus_voltage        # Voltaje en V
    shunt_voltage = ina.shunt_voltage    # Voltaje shunt en mV
    current = ina.current                # Corriente en mA
    power = ina.power                    # Potencia en mW
    
    print(f"Lectura {i+1}:")
    print(f"  Voltaje: {bus_voltage:.3f} V")
    print(f"  Corriente: {current:.1f} mA")
    print(f"  Potencia: {power:.1f} mW")
    print("-" * 50)
    
    time.sleep(1)

print("Sensor INA219 funcionando!")
