'''
    Created 
    Responsible for connecting to and uploading image to Amazon S3
    Owner: MARSfarm Corporation
    Author: Jackie Zhong(zy99120@gmail.com) - 6/11/20
    Modified By: Henry Borska(henryborska@wustl.edu) - 8/4/21
    Modified By: Peter Webb(peter@marsfarm.com) - 11.11.22
'''

import glob
import os
import boto3
from Trial_Util import Trial
import time
from datetime import datetime
from Sys_Conf import IMAGE_DIR, S3_BUCKET

# Look specifically at phase data, as that carries the information on what the device should be doing
# COMMENTED OUT 11.16.22 --- DELETE IF NOT NEEDED ---- #phaseData = t.phases

#defining a function for an S3 connection
# THIS MAY BE CHANGED TO A CLASS IN THE FUTURE

def s3_upload(self)
    observation_date = datetime.now().timestamp()
    
# Try to get fields from Trial and calculate others required
    try:
        t = Trial()
        trial_id_num = t.trial_id
        trial_id = str(t.trial_id)
        device_id = str(t.device_id)
        observation_timestamp = formatDateObject(observation_date)
        start_timestamp = formatDateObject(t.trial_start_date)
        day_number = calculateDayNum(start_timestamp, observation_timestamp)
        print('Imported fields from ', trial_id, ' and calculated number of days: ', day_number)

    except Exception as e:
        print("Failure getting Trial info")
        print(str(e))

    try
        s3 = boto3.resource('s3')
        print('Uploading most recent image from this directory: ', IMAGE_DIR, 'into s3 Bucket: ', S3_BUCKET)
    except Exception as e:
        print('Connection to create s3_upload image upload error: ', e)

def selectImage(self, timestamp):
    try:
        list_of_files = glob.glob(IMAGE_DIR + '*')
        #print(list_of_files, 'list of files as an array')
        latest_file = max(list_of_files, key=os.path.getctime) #get the latest taken picture
        print('latest image selected for upload to S3: ', latest_file)
        data = open(latest_file, 'rb')
        name = os.path.basename(latest_file)
    except Exception as e:
        print(' failed due to: ', e)
   
def formatDateObject(self, timestamp):
    date = datetime.fromtimestamp(timestamp).isoformat()
    datetime_object = parser.parse(date)
    return datetime_object

def calculateDayNum(self, start_timestamp, observation_timestamp):
    # Calculate day of trial - assume base 0
    sd = datetime.fromtimestamp(start_timestamp)
    od = datetime.fromtimestamp(observation_timestamp)
    return abs((sd - od).days)


# Retitled from "main" to "image_upload" on 11/16/2022 by PW
def image_upload(current_time, device_id, trial_id, day_number):
    su = s3_upload()
    current_time = observation_timestamp
    trial_id = trial_id_num
    day_number = s3.day_number
    try:
        #If bucket was not public, we could also add credentials in here
        if trial_id_num != 0:
            s3.Bucket(S3_BUCKET).put_object(Key=name,
                                                           Body=data,
                                                           Metadata={'currTime':current_time,
                                                                     'device_id':device_id,
                                                                     'trial_id':trial_id,
                                                                     'day_number':day_number
                                                                    })
        else:
             s3.Bucket(S3_BUCKET).put_object(Key=name,
                                                           Body=data,
                                                           Metadata={'currTime':current_time,
                                                                     'device_id':device_id,
                                                                     'day_number':day_number
                                                                    })
        #### ADD TEST LOG RECORD HERE
    except Exception as e:
        print('Image upload failed due to: ', e)

def test():
   print('Attempting S3 connection at: ', observation_date_string)
   print('connection to s3')
   s3 = s3_upload()
   s3.image_upload(su.observation_timestamp, su.device_id, su.trial_id_num, su.day_number)
    
if __name__ == "__main__":
    test()