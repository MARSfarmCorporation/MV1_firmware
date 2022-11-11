'''
class representation of the heater
This could be variable temperature, but here is either off or on
Author: Tyler Richards - 08.10.2021
Modified By: Howard Webb - 11/2/2022
'''
from pigpio import pi
from GPIO_Conf import HEATER, ON, OFF
from time import sleep
# pi needs to be defined outside the class
pi = pi()

class Heater:
    def __init__(self, gpio_pin):
        self.gpio = gpio_pin #Store heater GPIO
        pi.set_PWM_frequency(self.gpio,40000) #Set heater as 70kHz PWM channel
        pi.set_PWM_dutycycle(self.gpio,0) #Turn off heater when initialized
        
on(self):
       #PWM heater (ratio of 126/255: 50W)
       pi.set_PWM_dutycycle(HEATER,140)
       
    def off(self):
       pi.set_PWM_dutycycle(HEATER, OFF)
        
def test():
    print("Test Heater")
    h = Heater()
    print("Turn On")
    h.on()
    sleep(5)
    print("Turn Off")
    h.off()
    print("Done")

if __name__=="__main__":
    test()

