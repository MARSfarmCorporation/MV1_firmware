import Lights
import trial
import time
import datetime

lights = Lights.Light(26,5,13,19)

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

light_settings = current_phase['step'][1]['light_intensity']  # Store light settings are variable

# Variable to hold target light settings, dummy variable turns on red slightly to indicate error
target_light = [0, 10, 0, 0];

# Look through light array and find most up to date light setting
# NOTE: This only works if times are SORTED in ascending order in JSON
for i in range(len(light_settings)):

    if current_time.hour >= light_settings[i]['start_time'][0]:
        if current_time.minute >= light_settings[i]['start_time'][1]:
            target_light = light_settings[i]['setting']  # Save temp if the current time is greater than time from array

lights.customMode(target_light[0], target_light[1], target_light[2], target_light[3]) 


