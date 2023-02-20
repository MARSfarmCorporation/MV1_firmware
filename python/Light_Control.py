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
t_fr, t_r, t_b, t_w = t.get_light_values()

# Retrieve the current time for logging purposes
time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print('far red, red, blue, and white LED settings received', t_fr, t_r, t_b, t_w)
# V0.5 Brain PCBA Boards Only --- Modify light_intensity settings from recipe to be limited to max PWM possible without resistors exceeding 75C

# far-red
fr = 20
if(int(t_fr) < 20):
  fr = t_fr

# red
r = 120
if(int(t_r) < 120):
  r = t_r

# blue
b = 50
if(int(t_b) < 50):
  b = t_b

# white is not needed, 255 is under 75C
w = t_w

# Create light and set to current values
lights = Lights.Light()
lights.customMode(fr, r, b, w)
print('far red, red, blue, and white LED settings', fr, r, b, w, 'implemented at:', time)
