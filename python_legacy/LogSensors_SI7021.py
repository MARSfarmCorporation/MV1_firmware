"""
Log standard MVP sensors
Please run LogSensors.py OWITH PYTHON3!!!!!
-Specifically, the CO2 collection part, or MHZ16.py, will only work in Python3
-If want to run in Python2, get rid of all parts related to CO2 collection
    
Author: Howard Webb 
Modified by: Jackie Zhong(zy99120@gmail.com), Henry Borska - July 2021 - (HLB948@gmail.com), Tyler Richards(richardstylerj20@gmail.com)
"""

from Remote_MongoUtil import EnvironmentalObservation, insert_one
from SI7021 import *
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
ATTRIBUTE = "humidity"
UNIT = "%"
VALUE = 106


def log_sensors(test = False):
    
    
    sht=SHTC3()
    si=SI7021()
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
        status = 'Failure'
        #print(status)
        if test:
            status = 'Test'
    

    #Inserting temperature (C) into database
    try:
        temp = si.get_tempC()

        status = 'Success'
        #print(status)
        #print(temp)
        if test:
            status = 'Test'
        insert_one(EnvironmentalObservation(OBSERVATION_DATE, 'temperature', temp, 'C', TRIAL_ID, TRIAL_NAME, TRIAL_START_DATE))
        
    except Exception as e:
        status = 'Failure'
        #print(status)
        if test:
            status = 'Test'


    #Inserting humidity (%) into database
    try:
        humid = si.get_humidity()

        status = 'Success'
        #print(status)
        #print(humid)
        if test:
            status = 'Test'
        insert_one(EnvironmentalObservation(OBSERVATION_DATE, 'humidity', humid, '%', TRIAL_ID, TRIAL_NAME, TRIAL_START_DATE))
        
    except Exception as e:
        status = 'Failure'
        #print(status)
        if test:
            status = 'Test'

            

    #Update google sheets
    #this part is for google sheet update
    try:
        update_sheet('Environment_Observation', 'CO2', co2, 'ppm')
    except Exception as e:
        update_sheet('Environment_Observation_ERROR', 'CO2', 0, 'ppm')
    
    try:
        update_sheet('Environment_Observation', 'Temperature', temp, 'Celcius')
    except Exception as e:
        update_sheet('Environment_Observation_ERROR', 'Temperature', '0', 'Celcius')
    
    try:
        update_sheet('Environment_Observation', 'Humidity', humid, 'Percentage')
    except Exception as e:
        update_sheet('Environment_Observation_ERROR', 'Humidity', 0, 'Percentage')

def test():
    log_sensors(True)

if __name__=="__main__":
    log_sensors()    


