import pigpio

pi = pigpio.pi()

class Light:
    def __init__( self, gpio_pin_far_red, gpio_pin_red, gpio_pin_green, gpio_pin_blue, gpio_pin_white):
        self.gpioFarRed = gpio_pin_far_red #Store red GPIO
        self.gpioRed = gpio_pin_red #Store red GPIO
        self.gpioGreen = gpio_pin_green #Store green GPIO
        self.gpioBlue = gpio_pin_blue #Store blue GPIO
        self.gpioWhite = gpio_pin_white #Store white GPIO
        
        #Create brightness variables
        self.farred = 0;
        self.red = 0;
        self.green = 0;
        self.blue = 0;
        self.white = 0;
        
        #Setup PWM on selected pins
        pi.set_PWM_frequency(self.gpioFarRed,1000)
        pi.set_PWM_frequency(self.gpioRed,1000)
        pi.set_PWM_frequency(self.gpioGreen,1000)
        pi.set_PWM_frequency(self.gpioBlue,1000)
        pi.set_PWM_frequency(self.gpioWhite,1000)

        #Turn off lights if they were on
        pi.set_PWM_dutycycle(self.gpioFarRed,0)
        pi.set_PWM_dutycycle(self.gpioRed,0)
        pi.set_PWM_dutycycle(self.gpioGreen,0)
        pi.set_PWM_dutycycle(self.gpioBlue,0)
        pi.set_PWM_dutycycle(self.gpioWhite,0)
        
    #Turn fan on and off
    def setState(self,state):
        if state != 0:
            pi.set_PWM_dutycycle(self.gpioFarRed,self.farred)
            pi.set_PWM_dutycycle(self.gpioRed,self.red)
            pi.set_PWM_dutycycle(self.gpioGreen,self.green)
            pi.set_PWM_dutycycle(self.gpioBlue,self.blue)
            pi.set_PWM_dutycycle(self.gpioWhite,self.white)
        else :
            pi.set_PWM_dutycycle(self.gpioFarRed,0)
            pi.set_PWM_dutycycle(self.gpioRed,0)
            pi.set_PWM_dutycycle(self.gpioGreen,0)
            pi.set_PWM_dutycycle(self.gpioBlue,0)
            pi.set_PWM_dutycycle(self.gpioWhite,0)
    
    #Off Mode
    def modeZero(self):
        #Set light variables
        self.farred = 0;
        self.red = 0;
        self.green = 0;
        self.blue = 0;
        self.white = 0;
        
        self.setState(1) #Push to light
        
    #High Blue mode
    def modeOne(self):
        self.farred = 0;
        self.red = 83;
        self.green = 85;
        self.blue = 109;
        self.white = 93;
        
        self.setState(1)
        
    #High Red Mode
    def modeTwo(self):
        self.farred = 0;
        self.red = 143;
        self.green = 86;
        self.blue = 80;
        self.white = 93;
        
        self.setState(1)

    #Less Red Mode
    def modeThree(self):
        self.farred = 0;
        self.red = 117;
        self.green = 85;
        self.blue = 80;
        self.white = 93;
        
        self.setState(1)
        
    def setMode(self, mode):
        if mode == 0:
            self.modeZero()
        elif mode == 1:
            self.modeOne()
        elif mode == 2:
            self.modeTwo()
        elif mode == 3:
            self.modeThree()
            
    #Custom
    def customMode(self, f, r, g, b, w):
        self.farred = f;
        self.red = r;
        self.green = g;
        self.blue = b;
        self.white = w;
        
        self.setState(1)
            
            

            
