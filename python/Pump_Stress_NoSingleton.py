import pigpio
import time
from GPIO_Conf import PUMP_GND, ON, OFF  # Import the pin number for the pump ground

# Create a single pigpio instance for the entire module
pi = pigpio.pi()

# Check if pigpio daemon is running
if not pi.connected:
    raise Exception("Failed to connect to pigpio daemon")

# File to log errors
LOG_FILE = "../logs/Pump_Stress_Log.log"

class Pump:
    def __init__(self):
        self.pi = pi  # Use the shared pigpio instance

    def on(self):
        self.pi.write(PUMP_GND, ON)

    def off(self):
        self.pi.write(PUMP_GND, OFF)

    def is_on(self):
        return self.pi.read(PUMP_GND) == ON

def stress_test():
    pump = Pump()

    try:
        # Set the pin high
        pump.on()
        time.sleep(0.1)
        if not pump.is_on():
            log_error("Failed to set pin high")

        # Set the pin low
        pump.off()
        time.sleep(0.1)
        if pump.is_on():
            log_error("Failed to set pin low")

    except Exception as e:
        log_error(f"Exception during stress test: {e}")

def log_error(message):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{time.ctime()}: {message}\n")

def cleanup():
    pi.stop()

if __name__ == "__main__":
    try:
        stress_test()
    finally:
        cleanup()  # Ensure pigpio is stopped at the end
