import pigpio
import time

# Pin and PWM settings
PIN = 21  # GPIO pin number
FREQUENCY = 50  # PWM frequency in Hz
DUTY_CYCLE = 255  # PWM duty cycle

# Create a single pigpio instance
pi = pigpio.pi()

# Check if pigpio daemon is running
if not pi.connected:
    raise Exception("Failed to connect to pigpio daemon")

def reset_pin_and_run_pwm():
    try:
        while True:
            # Reset the pin to output
            pi.set_mode(PIN, pigpio.OUTPUT)

            # Set the PWM frequency and duty cycle
            pi.set_PWM_frequency(PIN, FREQUENCY)
            pi.set_PWM_dutycycle(PIN, DUTY_CYCLE)

            # Short delay to prevent overloading the CPU
    except Exception as e:
        print(f"Exception occurred: {e}")
    finally:
        pi.stop()  # Ensure pigpio is stopped on exit

if __name__ == "__main__":
    reset_pin_and_run_pwm()
