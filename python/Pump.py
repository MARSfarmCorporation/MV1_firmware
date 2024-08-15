'''
class representation of the pump

Author: Tyler Richards - 09.10.2021
Modified By: Howard Webb - 11/2/2022

NOTE: The pump was designed to be reversable, but not implemented
needs more development to implement
'''

from PigpioManager import PigpioManager
from time import sleep
from pigpio import OUTPUT
from GPIO_Conf import PUMP_POS, PUMP_GND, ON, OFF

class Pump:
    # Initialize the pump object 
    def __init__(self, gpio_pinA=None, gpio_pinB=None):
        # get the pigpio instance
        self.pi = PigpioManager().get_pi()

        self.gpioA = PUMP_POS  # Store pump GPIO
        self.gpioB = PUMP_GND  # Store pump GPIO
        self.calibration = 0.7  # Rate of pumping, measured in ml/sec
        self.pi.set_mode(self.gpioA, OUTPUT)  # Set pump as output
        self.pi.set_mode(self.gpioB, OUTPUT)  # Set pump as output
        #self.off()  # Turn off pump when initialized

    def is_pumping(self):
        # Check if pump is currently pumping
        return pi.read(self.gpioA) == ON

    # Turn on the pump
    def on(self):
        self.pi.write(self.gpioA, OFF)
        self.pi.write(self.gpioB, ON)

    # Turn off the pump
    def off(self):
        self.pi.write(self.gpioA, OFF)
        self.pi.write(self.gpioB, OFF)

    # Dispense some user-defined amount of water
    def dispense(self, volume):
        if volume > 0:
            self.on()  # Begin pumping
            sleep(volume * self.calibration)  # Pump volume number of mL
            self.off()  # End pumping

# Test the pump class
def test():
    print("Test Pump")
    print('Pumping 10 ML as test')
    pump = Pump()
    pump.dispense(10)
    print("Done")

if __name__ == "__main__":
    test()
