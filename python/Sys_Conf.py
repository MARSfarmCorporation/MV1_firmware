'''
#Global variables for the system
Mostly directory paths
'''
#Complete DURING PROVISIONING
#- MARSfarm Serial Number:
#- Organization Name:
#- Provisioning Date:
#- Image Name:

#VARIABLES SET DURING PRODUCTION PROVISIONING

#Used for MQTT only - EVERYWHERE ELSE SHOULD USE Trial_Util.py
# ADD THIS TO S3 AS WELL
DEVICE_ID = '60f1a223786cb0a4a6a5a175'
# Example - DEVICE_ID = '60f1a223786cb0a4a6a5a175'
# Used for Remote_GoogleSheet.py
GOOGLE_SHEET_ID = '1MbRqOJNc0r9TPLMbF1aurRuqOKW9dOkEYR2dR2dP5Ps'
# Example GOOGLE_SHEET_ID = '1MbRqOJNc0r9TPLMbF1aurRuqOKW9dOkEYR2dR2dP5Ps'

#TBD ----- NOT WORKING YET Used for Ethernet Connection - may change this in cron instead
#MAC_ADDRESS =

#Variables below are not intended to change during provisioning

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
