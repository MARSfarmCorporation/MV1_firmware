'''
    MHZ16.py is responsible for connecting to and collecting data from the sensor
    The sensor is connected via a serial bus(UART). The communication proctocol is
    specified in the sensor documentation.

    !!! Please run MHZ16.py WITH PYTHON3!!!!!
    -If run with Python2, it may cause problem for LogSensors to interpret result.
    -This is due to an inability of data conversion from a bytearray to integer in Python2 automatically.

    Owner: MARSfarm Corporation
    Authors: Jackie Zhong(zy99120@gmail.com) - 6/30/20
    Modified By: Tyler Richards - 08.10.2021
    Modified By: Howard Webb - 11/2/2022
    Modified By: Peter Webb - 02/23/2023
'''

import serial
import string
import sys
import time

# open a serial connection to the sensor 
con = serial.Serial("/dev/ttyAMA0", 9600, timeout=5)

class MHZ16(object):

    def __init__(self):
        # open a serial connection to the sensor
        self.con = serial.Serial("/dev/ttyAMA0", 9600, timeout=5)
        self.counter = 0 # used for loop control of get_co2

    # send a command to the sensor to calibrate the span
    def calibrate_span(self):
        self.con.write(bytearray(b'\xff\x01\x88\x07\xd0\x00\x00\x00\xa0'))

    # send a command to the sensor to calibrate the zero point 
    def calibrate_zero(self):
        self.con.write(bytearray(b'\xff\x01\x87\x00\x00\x00\x00\x00\x78'))

    def get_co2(self):
       # get co2 value

       self.con.write(bytearray(b'\xff\x01\x86\x00\x00\x00\x00\x00\x79'))
       rcv = self.con.read(9)
       co2 = rcv[2] * 256 + rcv[3]
       #co2 = 20000
       #print(co2, self.counter)
       #if int(co2) > 3000 and self.counter < 5:
           #print(co2, self.counter)
           #self.counter += 1
           #there is danger of an infinite loop here
           #time.sleep(2)
           #self.get_co2()
       return co2

# tests the CO2 sensor 
def test():
    print("MHZ16 (Co2) Testing")
    c = MHZ16()
    co2 = c.get_co2()
    print("Co2 ppm:", co2)
    print("Done")

if __name__=="__main__":
    test()



