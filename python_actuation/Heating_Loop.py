import Heater
from SI7021 import *
import trial
import time
import datetime

heater = Heater.Heater(5)

si=SI7021()

# Import dictionary data
data = trial.trial

# Get current time
current_time = datetime.datetime.now()

# Get start date from JSON
start_date = data['start_date']

# Look specifically at phase data, as that carries the information on what the device should be doing
phaseData = data['phases']

current_phase = []
# Look through phase array
for i in range(len(phaseData)):
    # If current time is greater than the start day of the phase, then it is saved
    # Loop is continued until current time is less than start day of phase
    if time.time() > (phaseData[i]['phase_start'] * 86400) + start_date:
        current_phase = phaseData[i]  # Save specific phase data

temp_settings = current_phase['step'][0]['temperature']  # Store temperature settings as variable

target_temp = 0  # Variable to hold target temperature

# Look through temperature array and find most up to date temperature setting
# NOTE: This only works if times are SORTED in ascending order in JSON
for i in range(len(temp_settings)):

    if current_time.hour >= temp_settings[i]['start_time'][0]:
        if current_time.minute >= temp_settings[i]['start_time'][1]:
            target_temp = temp_settings[i]['setting']  # Save temp if the current time is greater than time from array

setpoint = (5/9)*(target_temp - 32)

temp = si.get_tempC()
# print(temp, "C")

if ( temp < setpoint): #Measured temp is below setpoint
    heater.setState(1) #Turn on heater to raise temp   

if ( temp > setpoint): #Measured temp is below setpoint
    heater.setState(0) #Turn off heater to lower temp

