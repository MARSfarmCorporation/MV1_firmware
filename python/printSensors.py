"""
Log standard MARSfarm Mini sensors
Please run LogSensors.py OWITH PYTHON3!!!!!
-Specifically, the CO2 collection part, or MHZ16.py, will only work in Python3
-If want to run in Python2, get rid of all parts related to CO2 collection
Author: Tyler Richards
"""

from SHTC3 import *
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
TRIAL_ID = data['_id'] # $oid

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
        print("CO2:")
        print(co2)
        if test:
            status = 'Test'

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

        print("TEMP:")
        print(temp)
        print("HUMIDITY:")
        print(humid)

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


def test():
    log_sensors(True)

if __name__=="__main__":
    log_sensors()
