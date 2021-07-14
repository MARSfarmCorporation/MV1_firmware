"""
Log standard MVP sensors
Please run LogSensors.py OWITH PYTHON3!!!!!
-Specifically, the CO2 collection part, or MHZ16.py, will only work in Python3
-If want to run in Python2, get rid of all parts related to CO2 collection
    
Author: Howard Webb 
Modified by: Jackie Zhong(zy99120@gmail.com), Henry Borska - July 2021 - (HLB948@gmail.com)
"""

from Remote_MongoUtil import EnvironmentalObservation, insert_one
from SI7021 import *
from GSheetUtil import update_sheet
from MHZ16 import get_co2
import serial
import string


#Hardcoded Data
TRIAL_NAME = "Test Trial 1"
TRIAL_ID = "60db520a1a0f29f5a74a0f62"
TRIAL_START_DATE = 1623621469
OBSERVATION_DATE = 1626195469 #change to date now 
ATTRIBUTE = "humidity"
UNIT = "%"
VALUE = 106


def log_sensors(test = False):

    si=SI7021()
    con = serial.Serial("/dev/ttyAMA0", 9600, timeout=5)
 
    #Inserting co2 (ppm) into database
    try:
        co2 = get_co2(con)
        if(int(co2) > 10000):
            co2 = get_co2(con)
        
        status = 'Success'
        if test:
            status = 'Test'
        insert_one(EnvironmentalObservation(OBSERVATION_DATE, 'co2', co2, 'ppm', TRIAL_ID, TRIAL_NAME, TRIAL_START_DATE))

    except Exception as e:
        status = 'Failure'
        if test:
            status = 'Test'
    

    #Inserting temperature (C) into database
    try:
        temp = si.get_tempC()

        status = 'Success'
        if test:
            status = 'Test'
        insert_one(EnvironmentalObservation(OBSERVATION_DATE, 'temperature', temp, 'C', TRIAL_ID, TRIAL_NAME, TRIAL_START_DATE))
        
    except Exception as e:
        status = 'Failure'
        if test:
            status = 'Test'


    #Inserting humidity (%) into database
    try:
        humid = si.get_humidity()

        status = 'Success'
        if test:
            status = 'Test'
        insert_one(EnvironmentalObservation(OBSERVATION_DATE, 'humidity', humid, '%', TRIAL_ID, TRIAL_NAME, TRIAL_START_DATE))
        
    except Exception as e:
        status = 'Failure'
        if test:
            status = 'Test'


    #Update google sheets
    update_sheet('Environment_Observation', 'Temperature', temp, 'Celcius')
    update_sheet('Environment_Observation', 'Humidity', humid, 'Percentage')
    update_sheet('Environment_Observation', 'CO2', co2, 'ppm')

def test():
    log_sensors(True)

if __name__=="__main__":
    log_sensors()    


