'''
Base class for all fans
No GPIO is defined here, it is set in the child class
Author: Tyler Richards - 07.15.2021 
Modified By: Howard Webb - 11/2/2022
'''
from PigpioManager import PigpioManager
from GPIO_Conf import ON, OFF

# define the base class for controlling fans 
class Fan_Class(object):
    
    def __init__(self):
        self.pi = PigpioManager().get_pi()
        self.pi.set_mode(self.gpio, OUTPUT) #Set fan as output
        # Set the GPIO pin mode as output for the fan
    
    def on(self):
        # Turn fan on (full speed)
        pi.write(self.gpio, ON)
        
    def off(self):
        # Turn fan off
        pi.write(self.gpio, OFF)