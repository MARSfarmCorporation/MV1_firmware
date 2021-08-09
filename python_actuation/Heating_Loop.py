import Heater
from SHTC3 import *
import trial
import time
import datetime
import Fan

exhaustFan = Fan.Fan(16)
circFan = Fan.Fan(20)

circFan.setState(1)

heater = Heater.Heater(21)

sht=SHTC3()

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

temp_settings = current_phase['step'][1]['temperature']  # Store temperature settings as variable
circ_settings = current_phase['step'][0]['circulation_fan']  # Store circulation fan settings as variable

target_temp = 0  # Variable to hold target temperature
target_fan = 1 # Variable to hold fan target

# Look through temperature array and find most up to date temperature setting
# NOTE: This only works if times are SORTED in ascending order in JSON
for i in range(len(temp_settings)):

    if ((current_time.hour*60) + current_time.minute) >= ((temp_settings[i]['start_time'][0]*60) + temp_settings[i]['start_time'][1]):
        target_temp = temp_settings[i]['setting']  # Save temp if the current time is greater than time from array

# Look through circ fan array and find most up to date setting
# NOTE: This only works if times are SORTED in ascending order in JSON
for i in range(len(circ_settings)):

    if ((current_time.hour*60) + current_time.minute) >= ((circ_settings[i]['start_time'][0]*60) + circ_settings[i]['start_time'][1]):
        target_fan = circ_settings[i]['setting']  # Save setting if the current time is greater than time from array

circFan.setState(target_fan) # Set circ fan state

setpoint = (5/9)*(target_temp - 32) # Convert F to C

temp = (sht.read_data())[0] # Get temp from SHTC3
print(temp, "C")

# Heater control code 
if ( temp < setpoint): #Measured temp is below setpoint
    heater.setState(1) #Turn on heater to raise temp   
    circFan.setState(1) # Set circ fan state

if ( temp > setpoint): #Measured temp is above setpoint
    heater.setState(0) #Turn off heater to lower temp

# Exhaust fan control code
if ( temp > setpoint + 1): #Measured temp is above setpoint by too much
    exhaustFan.setState(1) #Turn on exhaust fan
else:
    exhaustFan.setState(0) #Turn off fan

  
