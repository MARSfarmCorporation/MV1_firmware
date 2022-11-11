'''
Low level light abstraction
Author: Tyler Richards - 08.10.2021
Modified By: Howard Webb - 11/2/2022
'''
import pigpio
from GPIO_Conf import LIGHT_FAR_RED, LIGHT_RED, LIGHT_BLUE, LIGHT_WHITE
from time import sleep
# pi needs to be outside the class

pi = pigpio.pi()

class Light:
    def __init__( self, gpio_pin_far_red=0, gpio_pin_red=0, gpio_pin_blue=0, gpio_pin_white=0):
        # input parameters are ignored and may be removed in future release
        # wrapper for the four channel grow light pannel
        self.gpioFarRed = LIGHT_FAR_RED #Store red GPIO
        self.gpioRed = LIGHT_RED #Store red GPIO
        self.gpioBlue = LIGHT_BLUE #Store blue GPIO
        self.gpioWhite = LIGHT_WHITE #Store white GPIO
        
        #Create channel brightness variables
        self._farred = 0;
        self._red = 0;
        self._blue = 0;
        self._white = 0;
        
        #Setup PWM on selected pins
        pi.set_PWM_frequency(self.gpioFarRed,2000)
        pi.set_PWM_frequency(self.gpioRed,2000)
        pi.set_PWM_frequency(self.gpioBlue,2000)
        pi.set_PWM_frequency(self.gpioWhite,2000)

    #Turn light on and off
    def setState(self, state):
        # legacy function that should not be used
        if state != 0:
            # If else statements allow lights to turn off fully; Issue with PWM not shutting of LED's all the way
            pi.set_PWM_dutycycle(self.gpioFarRed, self._farred)
            pi.set_PWM_dutycycle(self.gpioRed, self._red)
            pi.set_PWM_dutycycle(self.gpioBlue, self._blue)
            pi.set_PWM_dutycycle(self.gpioWhite, self._white)
        else:
            pi.set_PWM_dutycycle(self.gpioFarRed, 0)
            pi.set_PWM_dutycycle(self.gpioRed, 0)
            pi.set_PWM_dutycycle(self.gpioBlue, 0)
            pi.set_PWM_dutycycle(self.gpioWhite, 0)
            
    def customMode(self, fr, r, b, w):
        # main function for setting lights
        pi.set_PWM_dutycycle(self.gpioFarRed, fr)
        pi.set_PWM_dutycycle(self.gpioRed, self._r)
        pi.set_PWM_dutycycle(self.gpioBlue, self._b)
        pi.set_PWM_dutycycle(self.gpioWhite, self._w)
        
    def white(self):
        self.customMode(0,0,0,255)        
        
    def off(self):
        self.customMode(0,0,0,0)
        
    def blink_blue(self):
        self.blink(0, 0, 100, 0)
        
    def blink_red(self):
        self.blink(0, 100, 0, 0)
        
    def blink(self, fr=0, r=0, b=0, w=100):
        # Used to indicate an error
        for i in range(0,5):
            self.customMode(fr, r, b, w)
            sleep(1)
            self.customMode(0,0,0,0)
            sleep(1)
        #Return light to previous settings
        import Light_On
        
def test():
    print("Light Test")
    # values are dummy, since not used
    light = Light()
    print("Turn on white")
    light.white()
    print("Blink Blue")
    light.blink_blue()
    sleep(3)
    print("Blink Red")
    light.blink_red()
    print("Blink (default White)")
    light.blink()
    print("Turn off")
    light.off()
    print("Done")

if __name__=="__main__":
    test()
