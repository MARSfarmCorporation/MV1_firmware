"""
SHTC3 humidity and temperature sensor
Technical notes of commands and operation and from:
https://www.mouser.com/datasheet/2/682/seri_s_a0003561073_1-2291167.pdf

Author : Tyler Richards - 08/09/2021
Modified By: Howard Webb -  11/2/2022
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

        #Split read command into array of 2 bytes then send. See read_command for full 16 bit value
        msgs = self._i2c.msg_write([0x78,0x66])
        # need a pause here between sending the request and getting the data
        time.sleep(1)
        
        #Read in the 6 byte output (2 temp bytes, one CRC temp byte, 2 humidity bytes, one CRC humidity byte)
        msgs = self._i2c.msg_read(6)
        
        if msgs == None:
            return None
        else:
            raw_temp = bytesToWord(msgs[0].data[0], msgs[0].data[1]) #Read out temp data
            raw_humidity = bytesToWord(msgs[0].data[3], msgs[0].data[4]) #Read out humidity data

        # decode data into human values according to data sheet:
        raw_temp = ((4375 * raw_temp) >> 14) - 4500 
        temperature = raw_temp / 100.0

        # repeat above steps for humidity data
        raw_humidity = (625 * raw_humidity) >> 12
        humidity = raw_humidity / 100.0

        return [temperature, humidity]
	
    def get_tempC_humidity(self):
        # return separated temperature and humidity values
        data = self.read_data()
        return data[0], data[1]
	
    def get_tempF_humidity(self):
        # return temperature in Fahrenheit and humidity values
        temperature, humidity = self.get_tempC_humidity()
        tempf = round((1.8 * temperature) + 32, 2)
        return tempf, humidity
	
def test():
    print("Test SHTC3")
    sensor = SHTC3()
    temp, humidity = sensor.get_tempC_humidity()
    print("TempC:", temp, "Humidity:", humidity)
    tempF, humidity = sensor.get_tempF_humidity()
    print("TempF:", tempF, "Humidity:", humidity)
    print("Done")
	
if __name__ == "__main__":
    test()
