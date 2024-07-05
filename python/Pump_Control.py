'''
Controller function for the pump class
Author: Tyler Richards - 05.10.2022
Modified By: Howard Webb - 11/2/2022
'''
import os
import time
from Trial_Util import Trial
from Pump import Pump
from datetime import datetime
from WebSocketUtil import devicedata_enqueue

#############################################
# Global Variables
#############################################

mqtt_topic = "devicedata"

#############################################
# Semaphores
#############################################

pump_lock_file = 'pump_lock.lock'
pump_lock_timeout = 750  # 750 seconds = 12.5 minutes

#############################################

# Import dictionary data
t = Trial()

# Get current time
time = datetime.now().strftime("%y-%m-%d %H:%M:%S")
observation_date = datetime.now().timestamp()

# creating an instance of the pump class
p = Pump()

# Check if the lock file exists and its timestamp
if os.path.exists(lock_file):
    with open(lock_file, 'r') as file:
        timestamp = float(file.read())
    # If the lock file is older than the timeout, ignore it
    if time.time() - timestamp < lock_timeout:
        print("Lock file exists and is valid. Skipping scheduled task.")
        exit()

# check to verify that pump is not already pumping to prevent overwrite
if p.is_pumping():
   print('Pump is already Pumping')
   exit

# retrieve pump settings from trial
ps = t.get_pump_setting()

p.dispense(ps) # dispensing specified amount of water
if (ps > 0):

    # Creating the payload via the enqueue function
    devicedata_enqueue(mqtt_topic,"pump", ps, "mL", observation_date, "PumpObservation")
    print('Pump dispersed ', ps, ' ML of water on ', time)

def test_pump(amount):
    p = Pump()

    # Check to verify that pump is not already pumping to prevent overwrite
    if p.is_pumping():
        print('Pump is already Pumping')
        return

    # Get current time
    observation_date = datetime.now().timestamp()

    p.dispense(amount) # Dispensing specified amount of water

    if amount > 0:
        # Creating the payload via the enqueue function
        devicedata_enqueue(mqtt_topic,"pump", amount, "mL", observation_date, "PumpObservation")
        print('Test pump dispersed', amount, 'ML of water. This is likely due to user input from the Web Application, but could aslo be due to a test.')
