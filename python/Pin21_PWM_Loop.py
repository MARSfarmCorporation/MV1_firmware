import pigpio
import time

PIN = 21  # GPIO pin for the heater
FREQUENCY = 50  # PWM frequency in Hz
DUTY_CYCLE = 255  # PWM duty cycle (100%)

pi = pigpio.pi()

if not pi.connected:
    raise Exception("Failed to connect to pigpio daemon")

try:
    while True:
        # Reset the pin to output mode and apply PWM settings
        pi.set_mode(PIN, pigpio.OUTPUT)
        pi.set_PWM_frequency(PIN, FREQUENCY)
        pi.set_PWM_dutycycle(PIN, DUTY_CYCLE)

        # Brief sleep to simulate timing
        time.sleep(0.1)

except Exception as e:
    print(f"Exception occurred: {e}")
finally:
    pi.stop()  # Ensure pigpio is stopped on exit
