import pigpio
import time
from GPIO_Conf import EXHAUST_FAN, HEATER_PWM  # Import the pin number and duty cycle for the exhaust fan

# Create a single pigpio instance for the entire module
pi = pigpio.pi()

# Check if pigpio daemon is running
if not pi.connected:
    raise Exception("Failed to connect to pigpio daemon")

# File to log errors
LOG_FILE = "../logs/Fan_Stress_Log.log"

class Fan:
    def __init__(self):
        self.pi = pi  # Use the shared pigpio instance
        self.pi.set_PWM_frequency(EXHAUST_FAN, 4000)  # Set PWM frequency to 4,000 Hz

    def on(self):
        self.pi.set_PWM_dutycycle(EXHAUST_FAN, HEATER_PWM)  # Set the PWM duty cycle

    def off(self):
        self.pi.set_PWM_dutycycle(EXHAUST_FAN, 0)  # Turn off the PWM signal

    def is_on(self):
        return self.pi.get_PWM_dutycycle(EXHAUST_FAN) == HEATER_PWM

def stress_test():
    fan = Fan()

    try:
        # Set the pin high (PWM on)
        fan.on()
        time.sleep(0.1)
        if not fan.is_on():
            log_error("Failed to set PWM high")
        time.sleep(10)  # Wait for 10 seconds

        # Set the pin low (PWM off)
        fan.off()
        time.sleep(0.1)
        if fan.is_on():
            log_error("Failed to set PWM low")
        time.sleep(10)  # Wait for 10 seconds

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
