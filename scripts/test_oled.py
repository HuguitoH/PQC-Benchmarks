"""
SSD1306 OLED display validation script.

Renders a test screen on a 128×64 OLED connected via I2C at address 0x3C.
Requires Raspberry Pi 5 with the display wired to the I2C bus.

Usage:
    python scripts/test_oled.py
"""

import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw

_OLED_WIDTH  = 128
_OLED_HEIGHT = 64
_I2C_ADDR    = 0x3C

_LINES = [
    "Quantum Lab",
    "Raspberry Pi 5",
    "Setup OK!",
    "Hugo H.M. — TFG 2026",
]
_LINE_HEIGHT = 16   # pixels between lines


def build_test_image(width: int, height: int) -> Image.Image:
    """Render test text onto a 1-bit image."""
    image = Image.new("1", (width, height))
    draw  = ImageDraw.Draw(image)
    for i, line in enumerate(_LINES):
        draw.text((0, i * _LINE_HEIGHT), line, fill=255)
    return image


def main() -> None:
    """Validate OLED display by rendering a test screen."""
    i2c  = busio.I2C(board.SCL, board.SDA)
    oled = adafruit_ssd1306.SSD1306_I2C(_OLED_WIDTH, _OLED_HEIGHT, i2c, addr=_I2C_ADDR)

    oled.fill(0)
    oled.show()

    image = build_test_image(oled.width, oled.height)
    oled.image(image)
    oled.show()

    print("OLED display OK")


if __name__ == "__main__":
    main()
