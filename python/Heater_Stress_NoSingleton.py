import pigpio
import time
from GPIO_Conf import HEATER  # Import the pin number for the heater

# Create a single pigpio instance for the entire module
pi = pigpio.pi()

# Check if pigpio daemon is running
if not pi.connected:
    raise Exception("Failed to connect to pigpio daemon")

# File to log errors
LOG_FILE = "../logs/Heater_Stress_Log.log"

class Heater:
    def __init__(self):
        self.pi = pi  # Use the shared pigpio instance

    def on(self):
        self.pi.write(HEATER, 1)

    def off(self):
        self.pi.write(HEATER, 0)

    def is_on(self):
        return self.pi.read(HEATER) == 1

def stress_test():
    heater = Heater()

    try:
        # Set the pin high
        heater.on()
        time.sleep(0.1)
        if not heater.is_on():
            log_error("Failed to set pin high")

        # Set the pin low
        heater.off()
        time.sleep(0.1)
        if heater.is_on():
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
