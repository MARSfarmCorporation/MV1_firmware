'''
comprehensive test of all major systems
Date: 11/1/2022
Author: Howard Webb
'''
print("\System Configuration Testing")

# importing and testing the 'test' function from the 'Trial_Util' module 
from Trial_Util import test
test()

# Sys_Conf - print key variables 

print("\nActuator Testing")

from Circulation_Fan import test
test()

from Exhaust_Fan import test
test()

from Heater import test
test()

from Lights import test
test()

from Pump import test
test()

#-----Sensor Testing-----#
print("\nSensor Testing")

from SHTC3 import test
test()

from MHZ16 import test
test()

import CameraAF
#test()

#---Cloud Communications---#
print("\nCloud Communications")

#add testing for ethernet

#add testing for wifi

#add testing for mqtt

from Remote_S3Util import test
test()

#print("Test Google Sheet Connection")
#from GSheetUtil import test
#test()

#MongoDB test

print("Log Sensors")
from LogSensors import test
test()

#---Controler functions---#
print("\nController Functions")

from Thermostat import test
test()

# Function, not object
import Light_Control

import Pump_Control

print("Testing Complete")
