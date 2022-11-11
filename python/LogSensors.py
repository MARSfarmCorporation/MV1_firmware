"""
Log standard MARSfarm Mini sensors
Please run LogSensors.py OWITH PYTHON3!!!!!
-Specifically, the CO2 collection part, or MHZ16.py, will only work in Python3
-If want to run in Python2, get rid of all parts related to CO2 collection

Author: Jackie Zhong - 08.14.2020
Modified By Tyler Richards - 08.10.2021
Modified By Howard Webb - 11.10.2022
"""

from Remote_MongoUtil import EnvironmentalObservation, insert_one
from SHTC3 import SHTC3
from GSheetUtil import update_sheet
from MHZ16 import get_co2 as MHZ16
import serial
from datetime import datetime
from Trial_Util import Trial
from Lights import Light
from Log_Conf import TEMP, CO2, HUMIDITY, FAHRENHEIT, PPM, PERCENT

# Import dictionary data
t = Trial()

# Get current time
observation_date = datetime.now().timestamp()

def get_co2():
    con = serial.Serial("/dev/ttyAMA0", 9600, timeout=5)
    #accessing MHZ16 sensor using serial
    try:
        co2 = MHZ16(con)
        if(int(co2) > 3000):
            co2 = MHZ16(con)
    except Exception as e:
        print(e)
        co2 = 0
    return co2

def save_db(value, name, unit):
     try:
        insert_one(EnvironmentalObservation(observation_date, name, value, unit, t.trial_id, t.trial_name, t.start_date))
     except Exception as e:
        print(e)
        # if data does not save to database, LED will blink blue
        l = Light()
        l.blink_blue()

def get_temp_humidity():
    #accessing SHTC3 sensor to read temperature and humidity data
    try:
        sensor = SHTC3()
        temp, humid = sensor.get_tempF_humidity()
    except Exception as e:
        print(e)
        # if sensor does not return a value, LED will blink red
        l = Light()
        l.blink_red()
    return temp, humid

def save_google_sheet(name, value, unit):
    #Update google sheets with sensor data
    update_sheet('Environment_Observation', name, value, unit)

def test():
   print('starting test')
   print('testing get_co2 function')
   co2 =  get_co2()
   print("Co2", co2)
   print('testing get_temp_humidity function')
   temp, humid = get_temp_humidity()
   print("Temp", temp, "Humidity", humid)
   print('testing save_db function by sending Co2')
   save_db(CO2, co2, PPM)
   print('save temp and humidity data to database')
   save_db(TEMP, temp, FAHRENHEIT)
   print("Save Humidity")
   save_db(HUMIDITY, humid, PERCENT)
   print("Save Sheet Function")
   print("Save CO2")
   save_google_sheet(CO2, co2, PPM)
   print("Save Temp")
   save_google_sheet(TEMP, temp, FAHRENHEIT)
   print("Save Humidity")
   save_google_sheet(HUMIDITY, humid, PERCENT)
   print("Done")

if __name__=="__main__":
    test()