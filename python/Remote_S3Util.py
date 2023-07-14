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
from Lights import Light
import time
from datetime import datetime
from Sys_Conf import IMAGE_DIR, S3_BUCKET, DEVICE_ID

current_time = datetime.now().strftime('%Y-%m-%d_%H%M')
print('Attempting S3 connection at: ', current_time)
# Try to get device ID and trial ID from JSON
try:
    t = Trial()
    trial_id_num = t.trial_id
    trial_id = str(t.trial_id)
    #print('trial ID', trial_id_num,  'as string', trial_id)
    device_id = str(DEVICE_ID)
    #print('device ID', DEVICE_ID,  'as string', device_id)
    #print('bucket name', S3_BUCKET, 'image directory', IMAGE_DIR)
    sd = t.start_date
    od = datetime.now().timestamp()
    #print('sd', sd, 'od', od)
    sd2 = datetime.fromtimestamp(sd)
    od2 = datetime.fromtimestamp(od)
    #print('sd2', sd2, 'od2', od2)

    day_number_int = abs((sd2 - od2).days)

    #day_number_int = 7   # used for testing of day_number format for metadata upload --- test day options of 0, 3, 10, 45, 103)
    #print('day number', day_number_int)
    day_number_str_nozero = str(day_number_int)
    #print('day number string - NO ZERO', day_number_str_nozero)
    day_number_str = day_number_str_nozero.zfill(2)
    #print('day number string - WITH LEADING 0', day_number_str)

except Exception as e:
    print("Failure getting Trial info")
    print(str(e))

# Look specifically at phase data, as that carries the information on what the device should be doing
phaseData = t.phases

def main():

    try:
        s3 = boto3.resource('s3') # creating a connection to Amazon S3

        list_of_files = glob.glob(IMAGE_DIR + '*') # get a list of the files in the specified directory
        #print(list_of_files, 'list of files as an array')
        latest_file = max(list_of_files, key=os.path.getctime) #get the latest taken picture
        print('latest image selected for upload to S3: ', latest_file)
        data = open(latest_file, 'rb') # open the latest file in binary mode
        name = os.path.basename(latest_file) # extract the name of the file 
        #print('data', data, 'name', name)
        
        #TO BE ADDED LATER FOR OPTIMIZATION OF S3 ACCESS
        s3_dir = (device_id + '/') # directory structure in S3 bucket
        s3_path = (s3_dir + name) # path of the file in S3 bucket
        #print('path of upload in s3: ', s3_path)

        #If bucket was not public, we could also add credentials in here
        # upload the file to S3 bucket with metadata
        if trial_id_num != 0:
            s3.Bucket(S3_BUCKET).put_object(Key=s3_path,
                                                           Body=data,
                                                           Metadata={
                                                                     'currTime':current_time,
                                                                     'device_id':device_id,
                                                                     'trial_id':trial_id,
								                                     'day_number':day_number_str,
                                                                    })
        else:
             s3.Bucket(S3_BUCKET).put_object(Key=s3_path,
                                                           Body=data,
                                                           Metadata={'currTime':current_time,
                                                                     'device_id':device_id,
                                                                    })
        print('image uploaded to this location', s3_path, 'in S3 bucket', S3_BUCKET)
        print('s3 image metadata uploaded Current Time: ', current_time, ' Device ID: ', device_id, 'Trial ID: ', trial_id, 'Day Number: ', day_number_str)

    except Exception as e:
        print('S3 upload failed due to: ', e)
        l = Light()
        l.blink_blue()

def test():
    main()
    print('S3 "main" function complete.')

if __name__ == "__main__":
    test()
