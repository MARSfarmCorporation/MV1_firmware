import pigpio

pi = pigpio.pi()

class Heater:
    def __init__(self, gpio_pin):
        self.gpio = gpio_pin #Store heater GPIO
        pi.set_mode(self.gpio, pigpio.OUTPUT) #Set heater as output
        pi.write(self.gpio,0) #Turn off heater when initialized
        
    #Turn on and off heater
    def setState(self, state):
        pi.write(self.gpio,state) #set fan to Heater