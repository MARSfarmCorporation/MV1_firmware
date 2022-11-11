'''
class representation of the pump

Author: Tyler Richards - 09.10.2021
Modified By: Howard Webb - 11/2/2022

NOTE: The pump was designed to be reversable, but not implemented
needs more development to implement
'''

import pigpio
import time

pi = pigpio.pi()


class Pump:
    def __init__(self, gpio_pinA, gpio_pinB):
        self.gpioA = gpio_pinA #Store pump GPIO
        self.gpioB = gpio_pinB #Store pump GPIO
        self.calibration = 0.7 ; #Rate of pumping, measured in ml/sec 
        pi.set_mode(self.gpioA, pigpio.OUTPUT) #Set pump as output
        pi.set_mode(self.gpioB, pigpio.OUTPUT) #Set pump as output
        pi.write(self.gpioA,0) #Turn off pump when initialized
        pi.write(self.gpioB,0) #Turn off pump when initialized
        
    #Directly turn on and off pump
    def setState(self, state):
    
        if (state == 1): #Forward
            pi.write(self.gpioA,1) #set pump to state
            pi.write(self.gpioB,0) #set pump to state
        elif (state == -1): #Backward
            pi.write(self.gpioA,0) #set pump to state
            pi.write(self.gpioB,1) #set pump to state
        else: #Stop pump
            pi.write(self.gpioA,0) #set pump to state
            pi.write(self.gpioB,0) #set pump to state
        
    #Dispense 10mL of water
    def calibrate(self):
        self.setState(1)#Begin pumping
        time.sleep(10*0.54);#Dispense 10mL
        self.setState(0) #End pumping
        
    #Dispense some user defined amount of water
    def dispense(self, volume):
        if (volume > 0):
            self.setState(1)#Begin pumping
            time.sleep(volume*self.calibration);#Pump volume number of mL
            self.setState(0) #End pumping
