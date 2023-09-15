'''
class representation of the heater
This could be variable temperature, but here is either off or on
pigpio must be set to sample rate of 1 microsecond in order to provide speed required for efficient use of Heater, done by cron now
Author: Tyler Richards - 08.10.2021
Modified By: Howard Webb - 11/2/2022
Modified By: Peter Webb w/advice from Tyler Richards - 11/21/2022
'''
from pigpio import pi
from GPIO_Conf import HEATER, ON, OFF, HEATER_PWM
from time import sleep
# pi needs to be defined outside the class
# set up a connection to the pigpio daemon
pi = pi()

# define a class for the heater
class Heater:
    def __init__(self):
        # intialize the heater in off state
        #We have to change sample rate to 1 microsecond so that it is able to provide a 40 KHz signal (faster switching of the heater)
        pi.set_PWM_frequency(HEATER,40000) #Set heater as 40kHz PWM channel 
        pi.set_PWM_dutycycle(HEATER,OFF) #Turn off heater when initialized
       
    def on(self):
       #turn on PWM heater (ratio of 126/255: 50W)
       pi.set_PWM_dutycycle(HEATER,HEATER_PWM)
       
    def off(self):
       # turn off the heater 
       pi.set_PWM_dutycycle(HEATER, OFF)

# tests the heater's functions        
def test():
    print("Test Heater")
    print("PWM frequency BEFORE initialization", pi.get_PWM_frequency(HEATER))
    h = Heater() # create an instance of the heater class
    print("PWM frequency AFTER initialization", pi.get_PWM_frequency(HEATER))
    print("Turn On")
    h.on()
    sleep(5) # wait for 5 seconds
    print("Turn Off")
    h.off()
    print("Done")

if __name__=="__main__":
    test()
