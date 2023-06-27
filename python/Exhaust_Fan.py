'''
Basic control of the exhaust fan
Inherites from Fan_Class
Will get invoked from Thermostat
Author: Howard Webb
Date: 11/2/2022
'''
from GPIO_Conf import EXHAUST_FAN
from Fan import Fan_Class
from time import sleep
from datetime import datetime, time

#subclass of Fan_Clas representing the exhaust fan
class Exhaust_Fan(Fan_Class):
    
    def __init__(self):
        # set GPIO for exhaust
        self.gpio = EXHAUST_FAN 
        super().__init__() #intialize parent class

# testing the exhaust fan functions
def test():
    print("Test Exhaust Fan")
    cf = Exhaust_Fan() #create an instance of exhaust fan
    print("Turn On")
    cf.on()
    sleep(5) # wait for 5 seconds
    print("Turn Off")
    cf.off()
    print("Done")

if __name__=="__main__":
    test()