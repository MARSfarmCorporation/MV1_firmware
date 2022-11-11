'''
comprehensive test of all major systems
Date: 11/1/2022
Author: Howard Webb
'''
from Trial_Util import test
test()

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

#---Controler functions---#
print("Controller Functions")

from Thermostat import test
test()

# Function, not object
import Light_Control

import Pump_Control

#---Cloud Communications---#

print("Log Sensors")
from LogSensors import test
test()

print("Take Picture")
import CameraAF

#add testing for mqtt

#add testing for ethernet

#add testing for wifi

print("Testing Complete")
