'''
    MHZ16.py is responsible for connecting to and collecting data from the sensor
    The sensor is connected via a serial bus(UART). The communication proctocol is
    specified in the sensor documentation.
    
    !!! Please run MHZ16.py WITH PYTHON3!!!!!
    -If run with Python2, it may cause problem for LogSensors to interpret result.
    -This is due to an inability of data conversion from a bytearray to integer in Python2 automatically.
    
    Owner: MARSfarm Corporation
    Authors: Jackie Zhong(zy99120@gmail.com)
    Last Modified: 6/30/20
'''

import serial
import string
import sys


con = serial.Serial("/dev/ttyAMA0", 9600, timeout=5)


def get_co2(con):
  con.write(bytearray(b'\xff\x01\x86\x00\x00\x00\x00\x00\x79'))
  rcv = con.read(9)
  return rcv[2] * 256 + rcv[3]
 

def calibrate_span(con):
  con.write(bytearray(b'\xff\x01\x88\x07\xd0\x00\x00\x00\xa0'))

def calibrate_zero(con):
  con.write(bytearray(b'\xff\x01\x87\x00\x00\x00\x00\x00\x78'))

if __name__=="__main__":
    print(get_co2(con))



