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

class Exhaust_Fan(Fan_Class):
    
    def __init__(self):
        # set GPIO for exhaust
        self.gpio = EXHAUST_FAN
        super().__init__()

def test():
    print("Test Exhaust Fan")
    cf = Exhaust_Fan()
    print("Turn On")
    cf.on()
    sleep(5)
    print("Turn Off")
    cf.off()
    print("Done")

if __name__=="__main__":
    test()