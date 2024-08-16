from PigpioManager import PigpioManager
from GPIO_Conf import HEATER, ON, OFF, HEATER_PWM
from time import sleep
import pigpio

# define a class for the heater
class Heater:
    def __init__(self):
        # get the pigpio instance
        self.pi = PigpioManager().get_pi()
        # initialize the heater in off state
        #We have to change sample rate to 1 microsecond so that it is able to provide a 40 kHz signal (faster switching of the heater)
        self.pi.set_PWM_frequency(HEATER, 40000)  # Set heater as 40kHz PWM channel
        self.pi.set_PWM_dutycycle(HEATER, OFF)  # Turn off heater when initialized

    def on(self):
        # turn on PWM heater (ratio of 126/255: 50W)
        self.pi.set_PWM_dutycycle(HEATER, HEATER_PWM)

    def off(self):
        # turn off the heater
        self.pi.set_PWM_dutycycle(HEATER, OFF)

    def is_on(self):
        # Check the actual physical state of the heater pin
        return self.pi.read(HEATER) == 1  # Returns True if the pin is high (heater is on)
    
    def reset_pin(self):
        # Reinitialize the pin as an output
        self.pi.set_mode(HEATER, pigpio.OUTPUT)
        
        # Optionally toggle the pin to ensure it's responding
        self.pi.write(HEATER, 1)  # Set pin high
        self.pi.write(HEATER, 0)  # Set pin low
        
        # Ensure the pin is set to the desired state (e.g., off)
        self.pi.write(HEATER, 0)  # Explicitly set pin low
        
        # Optionally, reset PWM if used
        self.pi.set_PWM_dutycycle(HEATER, 0)  # Set PWM duty cycle to 0
        self.pi.set_PWM_frequency(HEATER, 0)  # Set PWM frequency to 0 (turn off PWM)

# tests the heater's functions        
def test():
    print("Test Heater")
    print("PWM frequency BEFORE initialization", h.pi.get_PWM_frequency(HEATER))
    h = Heater()  # create an instance of the heater class
    print("PWM frequency AFTER initialization", h.pi.get_PWM_frequency(HEATER))
    print("Turn On")
    h.on()
    sleep(5)  # wait for 5 seconds
    print("Turn Off")
    h.off()
    print("Done")

if __name__ == "__main__":
    test()
