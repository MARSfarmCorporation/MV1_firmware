'''
#Global variables for the system
Mostly directory paths
'''
IMAGE_DIR = "/home/pi/Desktop/MV1_firmware/pictures/"
PYTHON_DIR = "/home/pi/Desktop/MV1_firmware/python/"


# Currently keeping images in the legacy location
#IMAGE_DIR = "/home/pi/Desktop/MV1_firmware/pictures/"

S3_BUCKET = 'henry-metadata-testing'

# Mongo settings
MONGODB_URI = "mongodb+srv://device_data-RW:TOtuVtPoO8ePI5Ms@testing.7ppqd.mongodb.net/web-application?retryWrites=true&w=majority"
DB_NAME = "web-application"
COLLECTION_NAME = "device-data"
