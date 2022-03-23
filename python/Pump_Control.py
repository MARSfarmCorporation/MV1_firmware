import Pump
import trial
import time
import datetime

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

pump_settings = current_phase['step'][2]['pump_mount']  # Store pump settings are variable

# Variable to hold target settings
target_pump = 0;

# Look through pump array and find most up to date pump setting
# NOTE: This only works if times are SORTED in ascending order in JSON
for i in range(len(pump_settings)):
    #Check array and see if it is time to dispense (could create problem, CHECK functionality)
    if ((current_time.hour*60) + current_time.minute) == ((pump_settings[i]['start_time'][0]*60) + pump_settings[i]['start_time'][1]): 
        target_pump = pump_settings[i]['setting']  # Save temp if the current time is equal to array time

pump = Pump.Pump(24,23) # Set GPIO pins and create pump object
pump.dispense(target_pump) # Tell pump object to dispense specified mL of water
