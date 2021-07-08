"""
Log standard MVP sensors

Please run LogSensors.py OWITH PYTHON3!!!!!
-Specifically, the CO2 collection part, or MHZ16.py, will only work in Python3
-If want to run in Python2, get rid of all parts related to CO2 collection
    
Author: Howard Webb
Modified by: Jackie Zhong(zy99120@gmail.com)
"""

from SI7021 import *
from CouchUtil import saveList
from Remote_CouchUtil import saveList2
from GSheetUtil import update_sheet
from MHZ16 import get_co2
import serial
import string


def log_sensors(test = False):

    si=SI7021()
    
    con = serial.Serial("/dev/ttyAMA0", 9600, timeout=5)
 
    try:
        co2 = get_co2(con)
        if(int(co2) > 10000):
            co2 = get_co2(con)
        
        status = 'Success'
        if test:
            status = 'Test'
        saveList(['Environment_Observation', '', 'Top', 'Air', 'CO2', co2, 'ppm', 'MH-Z16', status, ''])
        saveList2(['Environment_Observation', '', 'Top', 'Air', 'CO2', co2, 'ppm', 'MH-Z16', status, '', ''])
        
        
    except Exception as e:
        status = 'Failure'
        if test:
            status = 'Test'
        saveList(['Environment_Observation', '', 'Top', 'Air', 'CO2', '', 'ppm', 'MH-Z16', status, str(e)])
        saveList2(['Environment_Observation', '', 'Top', 'Air', 'CO2', '', 'ppm', 'MH-Z16', status, str(e), ''])
    
    try:
        temp = si.get_tempC()

        status = 'Success'
        if test:
            status = 'Test'
        saveList(['Environment_Observation', '', 'Top', 'Air', 'Temperature', "{:10.1f}".format(temp), 'Farenheight', 'SI7021', status, ''])
        saveList2(['Environment_Observation', '', 'Top', 'Air', 'Temperature', "{:10.1f}".format(temp), 'Farenheight', 'SI7021', status, '', ''])
        
    except Exception as e:
        status = 'Failure'
        if test:
            status = 'Test'
        saveList(['Environment_Observation', '', 'Top', 'Air', 'Temperature', '', 'Farenheight', 'SI7021', status, str(e)])
        saveList2(['Environment_Observation', '', 'Top', 'Air', 'Temperature', '', 'Farenheight', 'SI7021', status, str(e), ''])

    try:
        humid = si.get_humidity()

        status = 'Success'
        if test:
            status = 'Test'
        saveList(['Environment_Observation', '', 'Top', 'Air', 'Humidity', "{:10.1f}".format(humid), 'Percent', 'SI7021', status, ''])
        saveList2(['Environment_Observation', '', 'Top', 'Air', 'Humidity', "{:10.1f}".format(humid), 'Percent', 'SI7021', status, '', ''])
        
    except Exception as e:
        status = 'Failure'
        if test:
            status = 'Test'
        saveList(['Environment_Observation', '', 'Top', 'Air', 'Humidity', '', 'Percent', 'SI7021', status, str(e)])
        saveList2(['Environment_Observation', '', 'Top', 'Air', 'Humidity', '', 'Percent', 'SI7021', status, str(e), ''])
    
    #this part is for google sheet update
    update_sheet('Environment_Observation', 'Temperature', temp, 'Celcius')
    update_sheet('Environment_Observation', 'Humidity', humid, 'Percentage')
    update_sheet('Environment_Observation', 'CO2', co2, 'ppm')

def test():
    log_sensors(True)

if __name__=="__main__":
    log_sensors()    
