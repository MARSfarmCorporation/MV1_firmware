'''
Controller function for the pump class
Author: Tyler Richards - 05.10.2022
Modified By: Howard Webb - 11/2/2022
'''
import os
import time as time_module  # Renamed to avoid conflict
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

pump_lock_file = '/home/pi/Desktop/MV1_firmware/python/pump_lock.lock'
pump_log_file = '/home/pi/Desktop/MV1_firmware/logs/Pump.log'
pump_lock_timeout = 750  # 750 seconds = 12.5 minutes

#############################################

def main():
    # Import dictionary data
    t = Trial()

    # Get current time
    current_time = datetime.now().strftime("%y-%m-%d %H:%M:%S")  # Renamed to avoid conflict
    observation_date = datetime.now().timestamp()

    # creating an instance of the pump class
    p = Pump()

    # Check if the lock file exists and its timestamp
    if os.path.exists(pump_lock_file):
        with open(pump_lock_file, 'r') as file:
            timestamp = float(file.read())
        # Logging the read timestamp
        with open(pump_log_file, 'a') as file:
            file.write(current_time + " - Read lock file timestamp: " + str(timestamp) + "\n")
        # If the lock file is older than the timeout, ignore it
        if time_module.time() - timestamp < pump_lock_timeout:
            # Log skipping the task due to valid lock file
            with open(pump_log_file, 'a') as file:
                file.write(current_time + " - Lock file exists and is valid. Skipping scheduled task.\n")
            print("Lock file exists and is valid. Skipping scheduled task.")
            return
        else:
            # Log ignoring the stale lock file
            with open(pump_log_file, 'a') as file:
                file.write(current_time + " - Lock file is stale. Continuing with scheduled task.\n")
            print("Lock file is stale. Continuing with scheduled task.")

    # Check to verify that pump is not already pumping to prevent overwrite
    if p.is_pumping():
        with open(pump_log_file, 'a') as file:
            file.write(current_time + " - Pump is already Pumping\n")
        print('Pump is already Pumping')
        return

    # Retrieve pump settings from trial
    ps = t.get_pump_setting()

    p.dispense(ps)  # Dispensing specified amount of water
    if ps > 0:
        # Creating the payload via the enqueue function
        devicedata_enqueue(mqtt_topic, "pump", ps, "mL", observation_date, "PumpObservation")
        with open(pump_log_file, 'a') as file:
            file.write(current_time + ' - Pump dispersed ' + str(ps) + ' ML of water.\n')
        print('Pump dispersed ', ps, ' ML of water on ', current_time)

def test_pump(amount):
    p = Pump()

    # Check to verify that pump is not already pumping to prevent overwrite
    if p.is_pumping():
        with open(pump_log_file, 'a') as file:
            file.write(datetime.now().strftime("%y-%m-%d %H:%M:%S") + " - Pump is already Pumping\n")
        print('Pump is already Pumping')
        return

    # Get current time
    current_time = datetime.now().strftime("%y-%m-%d %H:%M:%S")  # Renamed to avoid conflict
    observation_date = datetime.now().timestamp()

    # Create the lock file with a timestamp
    with open(pump_lock_file, 'w') as file:
        file.write(str(time_module.time()))

    p.dispense(amount)  # Dispensing specified amount of water

    if amount > 0:
        # Creating the payload via the enqueue function
        devicedata_enqueue(mqtt_topic, "pump", amount, "mL", observation_date, "PumpObservation")
        with open(pump_log_file, 'a') as file:
            file.write(current_time + " - Test pump dispersed " + str(amount) + " mL of water.\n")
        print('Test pump dispersed', amount, 'ML of water. This is likely due to user input from the Web Application, but could also be due to a test.')

if __name__ == "__main__":
    main()
