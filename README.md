# MarsFarmMini

Scripts and code related to running the new implementation of the MarsFarm datalogging software
This all runs locally on a provisioned Raspberry Pi

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
