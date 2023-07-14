'''
Controller function for the Lights
Author: Tyler Richards - 08.10.2021
Modified By: Howard Webb - 11/2/2022
Modified By: Peter Webb - 02/1/2023 - V0.5 Brain Hardware - Set max light_intensity of (20,120,50,255) to prevent overheating (50C) of LED resistors.
Modified By: Peter Webb - 04/2/2023 - V0.6 Brain Hardware - Set max light_intensity of (????) to prevent overheating (50C) of LED resistors.
'''
import Lights
from Trial_Util import Trial
from GPIO_Conf import MAX_FAR_RED, MAX_RED, MAX_BLUE, MAX_WHITE
from datetime import datetime

t = Trial() # create an instance of the trial class
# Get currrent light settings
t_fr, t_r, t_b, t_w = t.get_light_values()

# Retrieve the current time for logging purposes
time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print('far red, red, blue, and white LED settings received', t_fr, t_r, t_b, t_w)
# V0.5 Brain PCBA Boards Only --- Modify light_intensity settings from recipe to be limited to max PWM possible without resistors exceeding 75C

# far-red
fr = MAX_FAR_RED
if(int(t_fr) < MAX_FAR_RED):
  fr = t_fr

# red
r = MAX_RED
if(int(t_r) < MAX_RED):
  r = t_r

# blue
b = MAX_BLUE
if(int(t_b) < MAX_BLUE):
  b = t_b

# white is not needed, 255 is under 75C
w = MAX_WHITE
if(int(t_b) < MAX_WHITE):
  w = t_w


# Create light and set to current values
def test():
    lights = Lights.Light()
    lights.customMode(fr, r, b, w)
    print('far red, red, blue, and white LED settings', fr, r, b, w, 'implemented at:', time)

if __name__=='__main__':
    test()