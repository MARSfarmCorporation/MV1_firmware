from PigpioManager import PigpioManager
import pigpio  # Ensure pigpio is imported for constants
import time
from GPIO_Conf import PUMP_GND  # Import the pin number for the pump

# Pin to be tested
PIN = PUMP_GND  # Replace with actual GPIO pin number

# File to log errors
LOG_FILE = "../logs/Pump_Stress_Log.log"

def stress_test():
    pi = PigpioManager().get_pi()

    try:
        # Set the pin high
        pi.write(PIN, 1)
        time.sleep(0.1)
        if pi.read(PIN) != 1:
            log_error("Failed to set pin high")

        # Set the pin low
        pi.write(PIN, 0)
        time.sleep(0.1)
        if pi.read(PIN) != 0:
            log_error("Failed to set pin low")

    except Exception as e:
        log_error(f"Exception during stress test: {e}")

def log_error(message):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{time.ctime()}: {message}\n")

if __name__ == "__main__":
    stress_test()
