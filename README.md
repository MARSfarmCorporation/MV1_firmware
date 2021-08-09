# MarsFarmMini

Scripts and code related to running the new implementation of the MarsFarm datalogging software
This all runs locally on a provisioned Raspberry Pi

## Python scripts and their function

### CameraAF
Sets the focal distance and orientation of the ArduCam and takes a photo. Also flashes the LED's white to while taking photo

### GSheetUtil
Utility for writing to google sheets

### I2CUtil
Utility for I2C communications

### LogSensors
Records sensor readings and sends them to MongoDB and Google sheets

### LogUtil
Now defunct/ unusable code that originally logged actions taken by Pi

### Remote_MongoUtil
Utility for sending data to MongoDB

### S3
Utility for sending photos to S3 bucket

### Heating_Loop
Reads trials.py to control the temperature and fans inside the unit

### Light_Control
Reads trials.py to control the lighting inside the unit

### Rainbow_2
Test program to show patterns on LED's

### boot_script
Program run by cron at boot to ensure RPI GPIO is configured for use

### trial
File that stores data from MQTT to define how the RPI should actuate the lights, fan, and heater

## Python classes and their function

### Lights
This class saves the PWM values for Far Red, Red, Blue, and White for each LED channel then actuates its GPIO pins

### Fan
This class actuates the GPIO pin associated with a fan

### Pump
This class, which is currently not in use, actuates an H-Bridge driven pump at its GPIO pins

### Heater
This class actuates the GPIO pin associated with a heater

### SI7021
This legacy class contains all of the methods that an SI7021 can perform (ie read temperature or read humidity)

### SHTC3
This new class contains all of the methods that an SHTC3 can perform (ie read temperature or read humidity)
