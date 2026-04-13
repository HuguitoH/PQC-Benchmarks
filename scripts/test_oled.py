#!/usr/bin/env python3
"""
Test de la pantalla OLED
"""

import board
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# Crear conexión I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Crear objeto de pantalla (128x64 pixels, dirección 0x3C)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

# Limpiar pantalla
oled.fill(0)
oled.show()

# Crear imagen
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)

# Dibujar texto
draw.text((0, 0), "Quantum Lab", fill=255)
draw.text((0, 16), "Raspberry Pi 5", fill=255)
draw.text((0, 32), "Setup OK!", fill=255)
draw.text((0, 48), "By Hugo H.M.", fill=255)

# Mostrar en pantalla
oled.image(image)
oled.show()

print("Pantalla OLED funcionando")
