"""
INA219 current sensor validation script.

Reads 5 voltage/current/power samples at 1-second intervals.
Requires Raspberry Pi 5 with INA219 connected via I2C at address 0x40.

Usage:
    python scripts/test_ina219.py
"""

import time
import board
import busio
from adafruit_ina219 import INA219

_SAMPLES    = 5
_SAMPLE_DELAY = 1.0   # seconds between readings
_I2C_ADDR   = 0x40


def read_sensor(ina: INA219) -> dict:
    """Read a single sample from the INA219 sensor."""
    return {
        'bus_voltage_v'  : ina.bus_voltage,
        'shunt_voltage_mv': ina.shunt_voltage,
        'current_ma'     : ina.current,
        'power_mw'       : ina.power,
    }


def print_sample(index: int, sample: dict) -> None:
    """Print a formatted sensor reading."""
    print(f"Reading {index}:")
    print(f"  Voltage : {sample['bus_voltage_v']:.3f} V")
    print(f"  Current : {sample['current_ma']:.1f} mA")
    print(f"  Power   : {sample['power_mw']:.1f} mW")
    print("-" * 50)


def main() -> None:
    """Validate INA219 sensor connectivity and readings."""
    i2c = busio.I2C(board.SCL, board.SDA)
    ina = INA219(i2c, addr=_I2C_ADDR)

    print("INA219 sensor validation")
    print("=" * 50)

    for i in range(1, _SAMPLES + 1):
        sample = read_sensor(ina)
        print_sample(i, sample)
        time.sleep(_SAMPLE_DELAY)

    print("INA219 OK")


if __name__ == "__main__":
    main()
