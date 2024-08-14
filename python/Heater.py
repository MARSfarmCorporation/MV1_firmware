from pigpio import pi
from GPIO_Conf import HEATER, ON, OFF, HEATER_PWM
from time import sleep

# pi needs to be defined outside the class
# set up a connection to the pigpio daemon
pi = pi()

# define a class for the heater
class Heater:
    def __init__(self):
        # initialize the heater in off state
        #We have to change sample rate to 1 microsecond so that it is able to provide a 40 kHz signal (faster switching of the heater)
        pi.set_PWM_frequency(HEATER, 40000)  # Set heater as 40kHz PWM channel
        pi.set_PWM_dutycycle(HEATER, OFF)  # Turn off heater when initialized

    def on(self):
        # turn on PWM heater (ratio of 126/255: 50W)
        pi.set_PWM_dutycycle(HEATER, HEATER_PWM)

    def off(self):
        # turn off the heater
        pi.set_PWM_dutycycle(HEATER, OFF)
        print("Heater Off")

    def is_on(self):
        # Check the actual physical state of the heater pin
        return pi.read(HEATER) == 1  # Returns True if the pin is high (heater is on)

# tests the heater's functions        
def test():
    print("Test Heater")
    print("PWM frequency BEFORE initialization", pi.get_PWM_frequency(HEATER))
    h = Heater()  # create an instance of the heater class
    print("PWM frequency AFTER initialization", pi.get_PWM_frequency(HEATER))
    print("Turn On")
    h.on()
    sleep(5)  # wait for 5 seconds
    print("Turn Off")
    h.off()
    print("Done")

if __name__ == "__main__":
    test()
