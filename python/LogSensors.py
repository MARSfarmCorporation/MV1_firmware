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
from MHZ16 import MHZ16
import serial
from datetime import datetime
from Trial_Util import Trial
from WebSocketUtil import enqueue
from Lights import Light
from Log_Conf import TEMP, DB_TEMP, CO2, DB_CO2, DB_HUMIDITY, HUMIDITY, FAHRENHEIT, PPM, PERCENT
import time

# Import dictionary data
# The 't' dictionary object is used to store trial information
t = Trial()

# Get current time
observation_date = datetime.now().timestamp()

def get_co2():
    #con = serial.Serial("/dev/ttyAMA0", 9600, timeout=5)
    #accessing MHZ16 sensor using serial
    try:
        co2Sensor = MHZ16() # initialize the MHZ16 CO2 sensor 
        co2 = co2Sensor.get_co2() # read CO2 data from the sensor 
        counter = 0 # COUNTER DOES NOT CURRENTLY WORK used for loop control of get_co2 to prevent error in first sensor reading
        #co2 = 20000 # used for testing control loop
        # check if CO2 reading is above a threshold and counter is within limit
        if int(co2) > 3000 and counter < 5:
            print(co2, counter)
            counter += 1
            co2 = 450
    except Exception as e:
        print(e)
        co2 = 500
    return co2

# save sensor data to the remote MongoDB database
def save_db(name, value, unit):
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
        temp, humid = sensor.get_tempF_humidity() # read the temperature and humidity sensor 
    except Exception as e:
        print(e)
        # if sensor does not return a value, LED will blink red
        l = Light()
        l.blink_red()
    return temp, humid

def save_google_sheet(name, value, unit):
    #Update google sheets with sensor data
    update_sheet('Environment_Observation', name, value, unit)

# perfrom a test of the sensor data logging 
def test():
   print('starting test at: ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
   print('testing get_co2 function')
   co2 = get_co2()
   print("Co2", co2)
   print('testing get_temp_humidity function')
   temp, humid = get_temp_humidity()
   print("Temp", temp, "Humidity", humid)
   print('testing save_db function by sending Co2')
   save_db(DB_CO2, co2, PPM)
   enqueue("co2", co2, "ppm", observation_date, "EnvironmentalObservation")
   print('save temp and humidity data to database')
   save_db(DB_TEMP, temp, FAHRENHEIT)
   enqueue("temperature", temp, "C", observation_date, "EnvironmentalObservation")
   print("Save Humidity")
   save_db(DB_HUMIDITY, humid, PERCENT)
   enqueue("humidity", humid, "%", observation_date,"EnvironmentalObservation")
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
