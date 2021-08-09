"""
Log standard MARSfarm Mini sensors
Please run LogSensors.py OWITH PYTHON3!!!!!
-Specifically, the CO2 collection part, or MHZ16.py, will only work in Python3
-If want to run in Python2, get rid of all parts related to CO2 collection

Author: Tyler Richards
"""

from Remote_MongoUtil import EnvironmentalObservation, insert_one
from SHTC3 import *
from GSheetUtil import update_sheet
from MHZ16 import get_co2
import serial
import string
import time


#Hardcoded Data
TRIAL_NAME = "Test Trial 1"
TRIAL_ID = "60db520a1a0f29f5a74a0f62"
TRIAL_START_DATE = 1623621469
OBSERVATION_DATE = time.time() #change to date now

def log_sensors(test = False):


    sht=SHTC3()
    con = serial.Serial("/dev/ttyAMA0", 9600, timeout=5)

    #Inserting co2 (ppm) into database
    try:
        co2 = get_co2(con)
        if(int(co2) > 10000):
            co2 = get_co2(con)

        status = 'Success'
        #print(status)
        #print(co2)
        if test:
            status = 'Test'
        insert_one(EnvironmentalObservation(OBSERVATION_DATE, 'co2', co2, 'ppm', TRIAL_ID, TRIAL_NAME, TRIAL_START_DATE))
    except Exception as e:
        print("fault")
        
        
    #Inserting humidity and temp into database
    try:
        sensor_data = sht.read_data()
        temp2 = sensor_data[0]
        humid2 = sensor_data[1]

        # insert_one(EnvironmentalObservation(OBSERVATION_DATE, 'humidity', humid, '%', TRIAL_ID, TRIAL_NAME, TRIAL_START_DATE))
        # insert_one(EnvironmentalObservation(OBSERVATION_DATE, 'temperature', temp, 'C', TRIAL_ID, TRIAL_NAME, TRIAL_START_DATE))
        #print(status)
        #print(humid)

    except Exception as e:
        print(e)

    #Update google sheets
    #this part is for google sheet update
    try:
        update_sheet('Environment_Observation', 'CO2', co2, 'ppm')
    except Exception as e:
        update_sheet('Environment_Observation_ERROR', 'CO2', 0, 'ppm')

    try:
        update_sheet('Environment_Observation', 'Temperature', temp2, 'Celcius')
    except Exception as e:
        update_sheet('Environment_Observation_ERROR', 'Temperature', '0', 'Celcius')

    try:
        update_sheet('Environment_Observation', 'Humidity', humid2, 'Percentage')
    except Exception as e:
        update_sheet('Environment_Observation_ERROR', 'Humidity', 0, 'Percentage')

def test():
    log_sensors(True)

if __name__=="__main__":
    log_sensors()


