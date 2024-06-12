'''
Name assignments for GPIO pins
Keep in order so can make sure not assigning two function to the same pin
Author:  Howard Webb - 11/2/2022
'''
from Sys_Conf import VERSION

# assigning the GPIO pin numbers to names for easier reference 
# the names indicate the function or purpose of the respective pin 

# Max PWM values
if VERSION == "V0.7":
  HEATER_PWM = 175
  MAX_FAR_RED = 100
  MAX_RED = 255
  MAX_BLUE = 200
  MAX_WHITE = 200
elif VERSION == "V0.6":
  HEATER_PWM = 140
  MAX_FAR_RED = 100
  MAX_RED = 255
  MAX_BLUE = 200
  MAX_WHITE = 200
elif VERSION == "V0.5":
  HEATER_PWM = 140
  MAX_FAR_RED = 0
  MAX_RED = 120
  MAX_BLUE = 50
  MAX_WHITE = 255
else:
  print("Version not set")
  HEATER_PWM = 0
  MAX_FAR_RED = 0
  MAX_RED = 0
  MAX_BLUE = 0
  MAX_WHITE = 0

LIGHT_RED = 5
LIGHT_BLUE = 13

CIRCULATION_FAN = 16
LIGHT_WHITE = 19
EXHAUST_FAN = 20
HEATER = 21
PUMP_POS = 23
PUMP_GND= 24
LIGHT_FAR_RED = 26

# Value settings for on and off
ON = 1
OFF = 0
