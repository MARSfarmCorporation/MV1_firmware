"""
SI7021 humidity and temperature sensor
Technical notes of commands and operation and from:
https://www.silabs.com/documents/public/data-sheets/Si7021-A20.pdf

 Author : Howard Webb
 Date   : 06/20/2018

"""

import time
from I2CUtil import I2C, bytesToWord

# Device I2C address
addr = 0x70
read_command = 0x7866


class SHTC3(object):

    def __init__(self):
        self._addr = addr
        self._i2c = I2C(addr)

    def read_data(self):
        # Reads both humidity and temp at the same time

        temp = None
        humidity = None

        msgs = self._i2c.msg_write([0x78,0x66])
        # need a pause here between sending the request and getting the data
        time.sleep(1)
        msgs = self._i2c.msg_read(6)
        
        if msgs == None:
            return None
        else:
            temp_data = [bytesToWord(msgs[0].data[0]), bytesToWord(msgs[0].data[1])]
            humidity_data = [bytesToWord(msgs[0].data[3]), bytesToWord(msgs[0].data[4])]

        # decode data into human values:
        # convert bytes into 16-bit signed integer
        # convert the LSB value to a human value according to the datasheet
        raw_temp = (temp_data[1] << 8) + temp_data[0]
        raw_temp = ((4375 * raw_temp) >> 14) - 4500
        temperature = raw_temp / 100.0

        # repeat above steps for humidity data
        raw_humidity = (humidity_data[1] << 8) + humidity_data[0]
        raw_humidity = (625 * raw_humidity) >> 12
        humidity = raw_humidity / 100.0
        
        print(temperature)
        print(humidity)
        return [temperature, humidity]

