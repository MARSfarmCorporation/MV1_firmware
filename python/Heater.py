import pigpio

pi = pigpio.pi()

class Heater:
    def __init__(self, gpio_pin):
        self.gpio = gpio_pin #Store heater GPIO
        pi.set_PWM_frequency(self.gpio,40000) #Set heater as 70kHz PWM channel
        pi.set_PWM_dutycycle(self.gpio,0) #Turn off heater when initialized
        
    #Turn on and off heater
    def setState(self, state):
        if (state > 0):
            pi.set_PWM_dutycycle(self.gpio,140) #PWM heater (ratio of 126/255: 50W)
        if (state == 0):
            pi.set_PWM_dutycycle(self.gpio,0) #PWM heater at 0
