'''
child class of speciliazed (curculation) fan
all functionality is in the parent class
Author: Howard Webb
Date: 11/2/2022
'''
from GPIO_Conf import CIRCULATION_FAN
from Fan import Fan_Class
from time import sleep

# define child class Circulation_Fan, which inherits from Fan
class Circulation_Fan(Fan_Class):
    
    def __init__(self):
        # set the GPIO for this fan
        self.gpio = CIRCULATION_FAN
        super().__init__() # call the parent class constructor 

# tests the circulation fan - my comment
def test():
    print("Test Circulation Fan")
    cf = Circulation_Fan() # create an instance of Circulation_Fan
    print("Turn On")
    cf.on() # turn on the fan
    sleep(30) # wait for 30 seconds
    print("Turn Off") 
    cf.off() # turn off the fan
    print("Done")

if __name__=="__main__":
    test() # call the test function if the script is run directly