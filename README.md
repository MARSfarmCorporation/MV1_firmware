# MarsFarmMini

Scripts and code related to running the new implementation of the MarsFarm datalogging software
This all runs locally on a provisioned Raspberry Pi

[Link to Catch All Board documentation](https://docs.google.com/document/d/1rYqv2FnSNgXrrBOkOoK7FdZ9B48B3JKYJkC4YfoGmYI/edit?usp=sharing)

[Link to Production Board documentation](https://docs.google.com/document/d/18hr8wcDvSWbsPwOnVfIchaOfuOhui3_LxkCoquSs5Wg/edit?usp=sharing)

[Link to Light Board documentation](https://docs.google.com/document/d/1j48XNIAOSjZMT99Io0jHe7IRb-LhJGaQ8D5Ax2oAHz0/edit?usp=sharing)


## Python scripts and their function

### CameraAF.py
Sets the focal distance and orientation of the ArduCam and takes a photo. Also flashes the LED's white to while taking photo

### GSheetUtil.py
Utility for writing to google sheets

### I2CUtil.py
Utility for I2C communications

### LogSensors.py
Records sensor readings and sends them to MongoDB and Google sheets

### LogUtil.py
Now defunct/ unusable code that originally logged actions taken by Pi

### Remote_MongoUtil.py
Utility for sending data to MongoDB

### S3.py
Utility for sending photos to S3 bucket

### Heating_Loop.py
Reads trials.py to control the temperature and fans inside the unit

### Light_Control.py
Reads trials.py to control the lighting inside the unit

### Rainbow_2.py
Test program to show patterns on LED's

### boot_script.py
Program run by cron at boot to ensure RPI GPIO is configured for use

### trial.py
File that stores data from MQTT to define how the RPI should actuate the lights, fan, and heater

## Python classes and their function

### Lights.py
This class saves the PWM values for Far Red, Red, Blue, and White for each LED channel then actuates its GPIO pins

### Fan.py
This class actuates the GPIO pin associated with a fan

### Pump.py
This class, which is currently not in use, actuates an H-Bridge driven pump at its GPIO pins

### Heater.py
This class actuates the GPIO pin associated with a heater

### SI7021.py
This legacy class contains all of the methods that an SI7021 can perform (ie read temperature or read humidity)

### SHTC3.py
This new class contains all of the methods that an SHTC3 can perform (ie read temperature or read humidity)
