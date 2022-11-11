'''
Controller function for the Lights
Author: Tyler Richards - 08.10.2021
Modified By: Howard Webb - 11/2/2022
'''
import Lights
from Trial_Util import Trial
from datetime import datetime

t = Trial()
# Get currrent light settings
fr, r, b, w = t.get_light_values()

# Retrieve the current time for logging purposes
time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print('far red, red, blue, and white LED settings received', fr, r, b, w)
# Create light and set to current values
lights = Lights.Light()
lights.customMode(fr, r, b, w)
print('lights set to trial settings at:', time)
