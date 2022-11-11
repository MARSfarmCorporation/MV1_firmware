'''
child class of speciliazed (curculation) fan
all functionality is in the parent class
Author: Howard Webb
Date: 11/2/2022
'''
from GPIO_Conf import CIRCULATION_FAN
from Fan import Fan_Class
from time import sleep

class Circulation_Fan(Fan_Class):
    
    def __init__(self):
        # set the GPIO for this fan
        self.gpio = CIRCULATION_FAN
        super().__init__()

    
def test():
    print("Test Circulation Fan")
    cf = Circulation_Fan()
    print("Turn On")
    cf.on()
    sleep(30)
    print("Turn Off")
    cf.off()
    print("Done")

if __name__=="__main__":
    test()