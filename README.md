# MarsFarmMini

Scripts and code related to running the new implementation of the MarsFarm datalogging software
This all runs locally on a provisioned Raspberry Pi

## Python scripts and their function 

### CameraAF.py
Sets the LEDs to white, the focal distance and orientation of the ArduCam then takes a photo. It also uses the current time to save the captured image. 

### Circulation_Fan.py
Inherits from the parent class, 'Fan_Class', representing a specialized circulation fan. It includes a 'test()' function that creastes an instance of 'Circulation_Fan', turnis it on for 30 seconds, and then turns it off, prodviding a simple test routine for the fan's functionaility. 

### Ethernet.py
Changes the MAC address of the 'eth0' interface at boot by excuting a command using the 'sudo macchange' tool. It retrieves the desired MAC address from a configuration file and provides logging information for the command execution. (Changes ID to connect to internet)

### Exhaust_Fan.py
Controls an exhaust fan, inheriting from the 'Fan_Class'. It includes a 'test()' function that turns the exhaust fan on, waits for 5 seconds, and then turns it off. 

### Fan.py
This class actuates the GPIO pin associated with a fan
Deifines a base class called 'Fan_Class' for controlling fans using GPIO pins. It includes methods to turn the fan on and off and intializes the GPIO pin mode. 

### GPIO_Conf.py
Assings name to GPIO pins on a Raspberry Pi for various components such as lights, fans, pump, and heater. It also sets values for turining thes components on and off, providing a convenient reference for controlling and managing the GPIO pins in a connected system. 

### GSheetUtil.py
Utility for writing to google sheets
Connects to Google Sheets API using service account credentials, authorizes the client, and updates a Google Sheet bu inesriting rows of data with timestamps and provided values. It provides a function ('update_sheet') to facilitate the insertion of data into the sheet. 

### Heater.py
This class actuates the GPIO pin associated with a heater.
Provides methods to turn the heater on and off using PWM signlas, and a test function that turns the hearter on for 5 seconds and then turning it off.

### I2CUtil.py
Utility for I2C communications.
Communicates with I2C devices by sending and receiving messages over the I2C bus. Key features include methods for sending and receiving messages, writing data to an I2C device, and a function to convert bytes to a word value. 

### Light_Control.py
Reads trials.py to control the lighting inside the unit.
Controller function that retreives current light settings, sets maximum light intensity values, and controls LED lights. Also, logs the implemented settings along with the current time.

### Lights.py
This class saves the PWM values for Far Red, Red, Blue, and White for each LED channel then actuates its GPIO pins.
Provides methods to set the state of the light, customize the light channels' brightness levels, turn on/off specific colors, and blink the light with various colors. Additionally, includes a test function to demonstrate the usage of the 'Light' class. 

### LogSensors.py
Records sensor readings and sends them to MongoDB and Google sheets.
Collects data from a C02 sensor (MHZ16) and a temperature and humidity sensor (SHTC3). The script saves the data to a remote MongoDB database, updates a Google Sheet, and performs a test operation. 

### MHZ16.py
Methods to calibrate the sensor, retrieve CO2 values, and a test function to demonstrate its usage. When executed, the script establishes a serial connection, retrieves the CO2 value, and prints it as the output. 

### MQTTsub_savetrial.py
The provided code is an MQTT client script that connects to a broker and subscirbes to a specific topic. It listens for incoming messages on that topic, writes the payload of the received message to a file, and prints a confirmation message. The script runs indefinetly, continuosly checking for new messages. 

### Pump_Control.py
Controller function for a pump class. Imports 'Trial' and 'Pump' classes, retrieves pump settings from a trial, checks if the pump is already pumping, and dispenses water based on the retrieved settings. It also prints a message with the amount of water dispenses and current time. 

### Pump.py
This class, which is currently not in use, actuates an H-Bridge driven pump at its GPIO pins
Controls a pump using GPIO pins. Methods to turn pump on/off, check if it's currently pumping, calibrate the pump to dispense a fixed amount of water, and dispense a user-defined volume of water. The code also includes a test function that creates an instance of the Pump class and tests the dispensing functionality by pumping 10mL of water. 

### Remote_MongoUtil.py
Utility for sending data to MongoDB
Connects to a MongoDB and has methods to format dates, calculate day and week numbers, and intialize its attirbutes. Function to insert a single observation into MongoDB and a test function.

### Remote_S3Util.py
Connects to Amazon S3 and uploads the latest image from a specified directory. It retrieves device and trial information, including metadata such as current time, deivce ID, trial ID and day number. The image is then uploaded to the S3 bucket with the corresponding metadata.  

### SHTC3.py
This new class contains all of the methods that an SHTC3 can perform (ie read temperature or read humidity).
Sensor for humididty and temperature with methods for doing so in Celsius and Fahrenheit. The code also includes a test function that demonstartes the usage of the sensor by retreiving and prinintg the temperature and humidity readings. 

### Sys_Conf.py
The code defines global variables used for system configuration, including MQTT communciation, file paths, S3 bucket, Google Sheets, and MongoDB connection details, These variables enable customization and provide necessary information for the system's functionality.

### Test.py
Tests various modules and functions related to system configuration, acuators, sensors, cloud communications, logging sensors, and controller functions, It imports the modules and executes the corresponding test functions to ensure proper functioning of these components. 

### Thermostat.py
Implements a basic thermostat using temperature and humidity sensor (SHTC3) readings to control a heater, circulation fan, and exhaust fan. It adjusts the temperature based on a setpoint, turning on the heater and circulation fan if the measured temperature is below the setpoint and turning on the exhaust fan if the temperature exceeds the setpoint by a certain threshold.

### Trial_Util.py
Accesses and manipulates trial data. Function to retrieve current phase information, light values, setpoints, fan settings, and pump settings, and a test function. 

### trial.py
File that stores data from MQTT to define how the RPI should actuate the lights, fan, and heater

## Python classes and their function

### SI7021.py
This legacy class contains all of the methods that an SI7021 can perform (ie read temperature or read humidity)

### LogUtil.py
Now defunct/ unusable code that originally logged actions taken by Pi

### S3.py
Utility for sending photos to S3 bucket

### Heating_Loop.py
Reads trials.py to control the temperature and fans inside the unit

### Rainbow_2.py
Test program to show patterns on LED's

### boot_script.py
Program run by cron at boot to ensure RPI GPIO is configured for use

### trial.py
File that stores data from MQTT to define how the RPI should actuate the lights, fan, and heater

Links to Documentation
========================

Product Design (MV1 only)
------------------------------
 * [MV1 - Google Drive Folder (contains all documentation from Summer 2021 onward: Hardware, Testing, Architecture, etc.)](https://drive.google.com/drive/folders/1UcjC2NI9v7W5HeeAPR9AMCb38wjZm8VN?usp=share_link)
  * [Diagram of entire Platform Architecture used for MV1 cloud: MongoDB, ExpressJS, ReactJS, and NodeJS (MERN) stack.](https://viewer.diagrams.net/?page-id=hUamuTZxWKs4uIfqG7RM&highlight=0000ff&edit=_blank&layers=1&nav=1&page-id=hUamuTZxWKs4uIfqG7RM#G1rRgNSRLPabvuNownhoeclYH5YoiKG7r2)
* [Diagram of MongoDB database architecture in draw.io](https://viewer.diagrams.net/?page-id=DcuP4mfnnl_cNMED-0Ec&highlight=0000ff&edit=_blank&layers=1&nav=1#G1rRgNSRLPabvuNownhoeclYH5YoiKG7r2)


Hardware Development (MV1 only)
---------------
 * [Link to Catch All Board documentation (not in use, only used for dev)](https://docs.google.com/document/d/1rYqv2FnSNgXrrBOkOoK7FdZ9B48B3JKYJkC4YfoGmYI/edit?usp=sharing)
 * [Link to Production Board documentation](https://docs.google.com/document/d/18hr8wcDvSWbsPwOnVfIchaOfuOhui3_LxkCoquSs5Wg/edit?usp=sharing)
 * [Link to Light Board documentation](https://docs.google.com/document/d/1j48XNIAOSjZMT99Io0jHe7IRb-LhJGaQ8D5Ax2oAHz0/edit?usp=sharing)
 * [Heater - Information about testing and PWM / Duty cycle testing](https://docs.google.com/spreadsheets/d/1oFypIiIQ0HYoV11vfTSYGfxm0bYe1QiJ11H3ZHgr-O8/edit#gid=429470365&range=A1:F50)

Firmware Development (general)
-----------------------
 * [How to push local changes from a device to GitHub:](https://docs.google.com/document/d/1OTJcv9fFAd6GHeW61mBx-h2aYH95D1KO2G71raPEueY/edit)
 * [Common UNIX commands used when doing development](https://docs.google.com/document/d/1t68rj5UdpKkYAFzWZ84S6eEUnVqLPd1YFjAgU8UK7nY/edit)

Production (MV1 only)
-------------------------------
 * [How to create a new image on an SD card:](https://docs.google.com/document/d/1T9UipJatjMiOfbb7ay2Nh2nFmTY30WOMuiv9827T_lU/edit)
 * [How to test a finished production unit:](https://docs.google.com/document/d/1GzynpzX5hZFJA4CGZxr--B0ZOYwjwGt2JWh8CyWko7g/edit)
