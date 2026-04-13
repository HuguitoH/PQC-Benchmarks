import subprocess
import psutil
import time
import board
import busio
from adafruit_ina219 import INA219

def get_cpu_temp() -> float:
    """Read CPU temperature in Celsius using vcgencmd."""
    try:
        temp = subprocess.check_output(
            ["vcgencmd", "measure_temp"]
            ).decode()

        temp_value = float(temp.split("=")[1].replace("'C\n", ""))
        return temp_value

    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        return None

_process = psutil.Process()

def get_process_memory_mb() -> float:
    """Get the memory usage of the current process in MB."""
    process_mem = _process.memory_info().rss / (1024**2)
    return process_mem

def get_system_memory_mb() -> float:
    """Get the system memory usage in MB."""
    system_mem = psutil.virtual_memory().used / (1024**2)
    return system_mem


def setup_ina219(addr: int = 0x40) -> INA219 | None:
    """Set up the INA219 sensor and return the instance."""
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        ina = INA219(i2c, addr=addr)
        return ina

    except Exception as e:
        print(f"Error configuring INA219: {e}")
        return None

def get_ina219_reading(ina: INA219 | None) -> float | None:
    """Get the current reading from the INA219 sensor."""
    if ina is None:
        return None

    try:
        return ina.current

    except OSError:
        return None

def wait_cooldown(seconds: float = 2) -> None:
    """Wait for a cooldown period to allow the system to stabilize."""
    time.sleep(seconds)
