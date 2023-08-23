'''
comprehensive test of all major systems
Date: 11/1/2022
Author: Howard Webb
'''

import sys
import boto3
from datetime import datetime
from Sys_Conf import S3_BUCKET, SERIAL_NUMBER, DEVICE_ID

# redirect print to log file, which is overwritten each time
sys.stdout = open('/home/pi/Desktop/MV1_firmware/logs/test_job_log.txt', 'w')
print("\System Configuration Testing")

try:
    # importing and testing the 'test' function from the 'Trial_Util' module 
    from Trial_Util import test
    test()


    # Sys_Conf - print key variables 

    print("\nActuator Testing")

    from Circulation_Fan import test
    test()

    from Exhaust_Fan import test
    test()

    from Heater import test
    test()

    from Lights import test
    test()

    from Pump import test
    test()

    #-----Sensor Testing-----#
    print("\nSensor Testing")

    from SHTC3 import test
    test()

    from MHZ16 import test
    test()

    import CameraAF
    #test()

    #---Cloud Communications---#
    print("\nCloud Communications")

    #add testing for ethernet

    #add testing for wifi

    #add testing for mqtt

    from Remote_S3Util import test
    test()

    #print("Test Google Sheet Connection")
    #from GSheetUtil import test
    #test()

    #MongoDB test

    print("Log Sensors")
    from LogSensors import test
    test()

    #---Controler functions---#
    print("\nController Functions")

    from Thermostat import test
    test()

    # Function, not object
    import Light_Control

    import Pump_Control

    print("Testing Complete")

except Exception as e:
    print("Test Failed")
    print(e)

# close log file and reset print
sys.stdout.close()
sys.stdout = sys.__stdout__

# upload log file to S3
try:
    current_time = datetime.now().strftime("%Y-%m-%d_%H%M")
    file_name = '/home/pi/Desktop/MV1_firmware/logs/test_job_log.txt'
    s3_dir = (DEVICE_ID + '/')
    s3_path = (s3_dir + current_time + '_test_job_log.txt')
    s3 = boto3.resource('s3')
    with open(file_name, 'rb') as file_content:
        s3.Bucket(S3_BUCKET).put_object(Key=s3_path, Body=file_content, Metadata={
            'currTime':current_time,
            'device_id':DEVICE_ID,
            'serial_number':SERIAL_NUMBER,
        })
    print('Test Job Log uploaded to S3: ', s3_path)
    print('Test Recorded')

except Exception as e:
    print("Failure uploading Test Job Log to S3")
    print(str(e))