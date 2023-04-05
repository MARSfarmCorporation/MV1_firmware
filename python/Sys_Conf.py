'''
#Global variables for the system
Mostly directory paths
'''
#Complete DURING PROVISIONING
#- Image Creation Date: 04.05.23
#- Image Name: Basil

#VARIABLES SET DURING PRODUCTION PROVISIONING

#Used for client_id in MQTT
SERIAL_NUMBER = 'MV1-BASIL'

#Used for MQTT only - EVERYWHERE ELSE SHOULD USE Trial_Util.py -- will ADD THIS TO S3 AS WELL
DEVICE_ID = '6423953c35c8a81c4d15e729'
# MQTT Device ID for "MV1-Basil"

# Used for Remote_GoogleSheet.py
GOOGLE_SHEET_ID = '10ed3ea0NzxGotbzXoLQ68f2Z93XeAJOMpBTi1FLEC70'
# Google Sheet for "MV1 - Google Sheet - MV1_firmware_Sage_02_24_23" https://docs.google.com/spreadsheets/d/10ed3ea0NzxGotbzXoLQ68f2Z93XeAJOMpBTi1FLEC70/edit#gid=0

# Used in Ethernet.py to assign new static MAC address
MAC_ADDRESS = '68:e1:70:23:b2:01'

#VARIABLES SET DURING IMAGE CREATION

#Directory Paths
IMAGE_DIR = "/home/pi/Desktop/MV1_firmware/pictures/"
PYTHON_DIR = "/home/pi/Desktop/MV1_firmware/python/"

# Currently keeping images in the legacy location
#IMAGE_DIR = "/home/pi/Desktop/MV1_firmware/pictures/"

S3_BUCKET = 'mv1-production'

# Mongo settings
MONGODB_URI = "mongodb+srv://device_data-RW:TOtuVtPoO8ePI5Ms@testing.7ppqd.mongodb.net/web-application?retryWrites=true&w=majority"
DB_NAME = "web-application"
COLLECTION_NAME = "device-data"
