import pigpio

pi = pigpio.pi()

class Heater:
    def __init__(self, gpio_pin):
        self.gpio = gpio_pin #Store heater GPIO
        pi.set_PWM_frequency(self.gpio,60) #Set heater as 1kHz PWM channel
        pi.set_PWM_dutycycle(self.gpio,0) #Turn off heater when initialized
        
    #Turn on and off heater
    def setState(self, state):
        if (state > 0):
            pi.set_PWM_dutycycle(self.gpio,150) #PWM heater
        if (state == 0):
            pi.set_PWM_dutycycle(self.gpio,0) #PWM heater at 0
