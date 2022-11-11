'''
Controller function for the pump class
Author: Tyler Richards - 05.10.2022
Modified By: Howard Webb - 11/2/2022
'''
from Trial_Util import Trial
from Pump import Pump
from datetime import datetime

# Import dictionary data
t = Trial()

# Get current time
time = datetime.now().strftime("%y-%m-%d %H:%M:%S")

p = Pump()

# check to verify that pump is not already pumping to prevent overwrite
if p.is_pumping():
   print('Pump is already Pumping')
   exit

# retrieve pump settings from trial
ps = t.get_pump_setting()

p.dispense(ps)
print('Pump dispersed ', ps, ' ML of water on ', time)
