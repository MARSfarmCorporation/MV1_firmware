import pigpio
import time

pi = pigpio.pi()


class Pump:
    def __init__(self, gpio_pinA, gpio_pinB):
        self.gpioA = gpio_pinA #Store pump GPIO
        self.gpioB = gpio_pinB #Store pump GPIO    
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
        self.setState(1)#Begin pumping
        time.sleep(volume * 0.54);#Pump volume number of mL
        self.setState(0) #End pumping
