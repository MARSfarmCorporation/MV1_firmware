import pigpio

pi = pigpio.pi()

class Fan:
    def __init__(self, gpio_pin):
        self.gpio = gpio_pin #Store fan GPIO
        pi.set_mode(self.gpio, pigpio.OUTPUT) #Set fan as output
        pi.write(self.gpio,0) #Turn off fan when initialized
        
    #Turn on and off fan
    def setState(self, state):
        pi.write(self.gpio,state) #set fan to state