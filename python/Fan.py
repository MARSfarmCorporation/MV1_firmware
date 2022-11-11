'''
Base class for all fans
No GPIO is defined here, it is set in the child class
NOTE: This fan is on or off, no variable speed setting
Variable speed can be done (see Test_Fan,py)
Author: Howard Webb
Date: 11/2/2022
'''
from pigpio import pi, OUTPUT
from GPIO_Conf import ON, OFF, CIRCULATION_FAN
from time import sleep
# pi must be here outside of class
pi = pi()

class Fan_Class(object):
    
    def __init__(self):
        self.pi = pi
        self.pi.set_mode(self.gpio, OUTPUT) #Set fan as output
    
    def on(self):
        # Turn fan on (full speed)
        pi.write(self.gpio, ON)
        
    def off(self):
        # Turn fan off
        pi.write(self.gpio, OFF)