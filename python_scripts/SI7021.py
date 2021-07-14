"""
SI7021 humidity and temperature sensor
Technical notes of commands and operation and from:
https://www.silabs.com/documents/public/data-sheets/Si7021-A20.pdf

 Author : Howard Webb
 Date   : 11/27/2020
 
"""


import time
from I2CUtil import I2C
#from LogUtil import Logger

class DataException(Exception):
    pass

path = "/dev/i2c-1"
# Device I2C address
addr = 0x40
rh_no_hold = 0xF5      # Use and do own time hold
previous_temp = 0xE0   # Works but should not use

rh_hold = 0xE5         # Not used
temp_hold = 0XE3       # Not used
temp_no_hold = 0xF3    # Use but do own hold
temp_from_rh = 0xE0    # Not used
reset_cmd = 0xFE       # Available
write_reg_1 = 0xE6     # Not used
read_reg_1 = 0xE7      # Not used
# Heater control
write_heater_reg = 0x51 # Not doing callibration and fancy stuff at this time
read_heater_reg = 0x11  # ditto
# Unique ID for this chip
read_id_1_1 = 0xFA     # Available option
read_id_1_2 = 0x0F     # Available option
read_id_2_1 = 0xFC     # Available option
read_id_2_2 = 0xC9     # Available option
# Firmware revision
firm_rev_1_1 = 0x84
firm_rev_1_2 = 0x88

class SI7021(object):

   def __init__(self, logger=None):
    
      self._addr = addr
      self._path = path
      self._logger = logger
      if logger == None:
          self._logger = Logger("SI7021", Logger.INFO, "/home/pi/python/logs/obsv.log")
      self._i2c = I2C(path, addr, self._logger)
          
 
   def calc_humidity(self, read):
      """Calculate relative humidity from sensor reading
           Args:
               read: the sensor value
           Returns:
               rh: calculated relative humidity
           Raises:
               None
      """
      rh = ((125.0*read)/65536.0)-6.0
      return rh

   def calc_temp(self, read):
      """Calculate relative humidity from sensor reading
           Args:
               read: the sensor value
           Returns:
               tempC: calculated temperature in Centigrade
           Raises:
               None
      """
      tempC = ((175.72*read)/65536.0)-46.85
      return tempC

   def get_tempC_prior(self):
       """Get the temperature from the prior humidity reading
           Args:
               None
           Returns:
               tempC: calculated temperature in Centigrade
           Raises:
               None
       """

       msgs = self._i2c.get_data([previous_temp], 0.03, 3)
       if msgs == None:
           raise DataException("No Prior Temp data")
       else:
           value = self._i2c.bytesToWord(msgs[0].data[0],msgs[0].data[1])
           tempC = self.calc_temp(value) 
           return round(tempC, 2)

   def get_humidity(self):
       """Get the humidity
           Args:
               None
           Returns:
               rh: calculated relative humidity
           Raises:
                None
       """
       msgs = self._i2c.get_data([rh_no_hold], 0.03, 2)
       value = self._i2c.bytesToWord(msgs[0].data[0], msgs[0].data[1])       
       if value == None:
           raise DataException("No Humidity data")
       else:
           rh = self.calc_humidity(value)
           return round(rh, 2)

   def get_tempC(self):
       """Get the temperature (new reading)
           Args:
               None
           Returns:
               tempC: calculated temperature in Centigrade
           Raises:
               None
       """
       msgs = self._i2c.get_data([temp_no_hold], 0.03, 3)
       value = self._i2c.bytesToWord(msgs[0].data[0], msgs[0].data[1])
       if value == None:
           raise NameError("No TempC data")
       else:
           return round(self.calc_temp(value), 2)
        
   def get_tempF(self):
       # Convert C to F and round to 2 decimals
       return round(self.get_tempC() * (9/5) + 32, 2)


   def get_rev(self):
       """Get the firmware revision number
           Args:
               None
           Returns:
               rev: coded revision number
           Raises:
               None
       """
       self._logger.info("\nGet Revision")
#       msgs = self._i2c.get_msg([firm_rev_1_1, firm_rev_1_2], 3)
       msgs = self._i2c.get_data([firm_rev_1_1, firm_rev_1_2], 0.03, 3)
       # Need to test, may error out on some conditions
       if not ((msgs is None) or (msgs[0].data is None)):
          rev = msgs[0].data[0]
          if rev == 0xFF:
              self._logger.info("version 1.0")
          elif rev == 0x20:
              self._logger.info("version 2.0")
          else:
              self._logger.error("Unknown")
       else:
          self._logger.error("No Revision Data Available")
          return rev        

   def get_id1(self):
       """Print the first part of the chips unique id
           Args:
               None
           Returns:
               None
           Raises:
                None
       """
       self._logger.info("\nGet ID 1")
       try:
           msgs = self._i2c.get_data([read_id_1_1, read_id_1_2], 0.05, 4)
           ret= msgs[0].data
           for data in ret:
               self._logger.info("ID: " + str(hex(data)))
       except Exception as e:
          self._logger.error("Error getting msgs " + str(e))

   def get_id2(self):
       """Print the second part of the chips unique id
           The device version is in SNA_3
           Args:
               None
           Returns:
               None
           Raises:
               None
       """
           
       self._logger.info("\nGet ID 2")
       msgs = self._i2c.get_data([read_id_2_1, read_id_2_2], 0.05, 4)
       ret= msgs[0].data
       for data in ret:
          self._logger.info("ID" + str(hex(data)))
       sna3 = msgs[0].data[0]
       if sna3 == 0x00:
           self._logger.info("Device: Engineering Sample")
       elif sna3 == 0xFF:
           self._logger.info("Device: Engineering Sample")       
       elif sna3 == 0x14:
           self._logger.info("Device: SI7020")
       elif sna3 == 0x15:
           self._logger.info("Device: SI7021")
       else:
           self._logger.error("Unknown")

   def reset(self):
       """Reset the device
           Args:
               None
           Returns:
               None
           Raises:
               None
       """
            
       self._logger.info("\nReset")
       rev_1 = self._i2c.msg_write([reset_cmd])
       self._logger.info("Reset: " + str(rev_1))
    
def test():
    """Exercise all the SI7021 functions
        Args:
            None
        Returns:
            None
        Raises:
            None
    """
    print("\nTest SI7021")
    si=SI7021()
    si._logger.setLevel(Logger.INFO)
    while True:
       try: 
          print("\nTemp C: {}".format(si.get_tempC()))
          print("Humidity: {}%".format(si.get_humidity()))
          print("Temp F: {}".format(si.get_tempF()))
       except Exception as e:
          print(e)
       time.sleep(5)
       
def validate():
    """Exercise all the SI7021 functions
        Args:
            None
        Returns:
            None
        Raises:
            None
   """
    print("Test SI701")
    si = SI7021()
    si._logger.setLevel(Logger.INFO)
    print("\nGet Humidity - no hold split")
    try:
        rh = si.get_humidity()        
        print('Humidity : %.2f %%' % rh)
    except Exception as e:
        print(e)
    print("\nTest Temp")
    try:
       temp = si.get_tempC()
       print('Temp C: {} C'.format(temp))                              
    except Exception as e:
        print(e)
        return

    print("\nTest Temp - prior")
    try:
       temp = si.get_tempC_prior()
       print('Temp C Prior: {} C'.format(temp))                              
    except Exception as e:
        print(e)
        return
    try:
        tempF = si.get_tempF()
        print("Temp F: {} F".format(tempF))
    except Exception as e:
        print(e)

    print("\nTest Reset")    
    si.reset()
    print("\nTest Revision")    
    si.get_rev()
    print("\nTest Get ID 1")        
    si.get_id1()
    print("\nTest Get ID 2")        
    si.get_id2()
    
if __name__ == "__main__":
    test()
