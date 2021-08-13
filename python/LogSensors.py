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
import trial
import Lights
import pigpio

pi = pigpio.pi()

# Import dictionary data
data = trial.trial

# Get current time
OBSERVATION_DATE = time.time() #change to date now

# Get start date from JSON
TRIAL_START_DATE = data['start_date']

#Hardcoded Data
TRIAL_NAME = data['trial_name']
TRIAL_ID = data['_id']['$oid'] # $oid

def log_sensors(test = False):


    sht=SHTC3()
    con = serial.Serial("/dev/ttyAMA0", 9600, timeout=5)

    #Inserting co2 (ppm) into database
    try:
        co2 = get_co2(con)
        if(int(co2) > 3000):
            co2 = get_co2(con)

        status = 'Success'
        #print(status)
        #print(co2)
        if test:
            status = 'Test'
        insert_one(EnvironmentalObservation(OBSERVATION_DATE, 'co2', co2, 'ppm', TRIAL_ID, TRIAL_NAME, TRIAL_START_DATE))
    except Exception as e:
        # Blink Blue LED's if sensor error
        lights = Lights.Light(26,5,13,19)

        #Record previous light settings
        farred = pi.get_PWM_dutycycle(26)
        red = pi.get_PWM_dutycycle(5)
        blue = pi.get_PWM_dutycycle(13)
        white = pi.get_PWM_dutycycle(19)
        
        #Blink Blue light 5 times at 50%
        for i in range(0,5):
            lights.customMode(0,0,100,0)
            sleep(1)
            lights.customMode(0,0,0,0)
            sleep(1)
        
        #Return light to previous settings
        lights.customMode(farred,red,blue,white)

        print(e)
        
        
    #Inserting humidity and temp into database
    try:
        sensor_data = sht.read_data()
        temp = sensor_data[0]
        humid = sensor_data[1]

        insert_one(EnvironmentalObservation(OBSERVATION_DATE, 'humidity', humid, '%', TRIAL_ID, TRIAL_NAME, TRIAL_START_DATE))
        insert_one(EnvironmentalObservation(OBSERVATION_DATE, 'temperature', temp, 'C', TRIAL_ID, TRIAL_NAME, TRIAL_START_DATE))
        #print(status)
        #print(humid)

    except Exception as e:
        # Blink Blue LED's if sensor error
        lights = Lights.Light(26,5,13,19)

        #Record previous light settings
        farred = pi.get_PWM_dutycycle(26)
        red = pi.get_PWM_dutycycle(5)
        blue = pi.get_PWM_dutycycle(13)
        white = pi.get_PWM_dutycycle(19)
        
        #Blink Blue light 5 times at 50%
        for i in range(0,5):
            lights.customMode(0,0,100,0)
            time.sleep(1)
            lights.customMode(0,0,0,0)
            time.sleep(1)
        
        #Return light to previous settings
        lights.customMode(farred,red,blue,white)
        
        print(e)

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


