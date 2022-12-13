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
from Sys_Conf import IMAGE_DIR, S3_BUCKET, DEVICE_ID

current_time = datetime.now().strftime('%Y-%m-%d_%H%M')
print('Attempting S3 connection at: ', current_time)
# Try to get device ID and trial ID from JSON
try:
    t = Trial()
    trial_id_num = t.trial_id
    trial_id = str(t.trial_id)
    device_id = str(DEVICE_ID)
    sd = t.start_date
    od = datetime.now().timestamp()
    #print('sd', sd, 'od', od)
    sd2 = datetime.fromtimestamp(sd)
    od2 = datetime.fromtimestamp(od)
    #print('sd2', sd2, 'od2', od2)

    day_number_int = abs((sd2 - od2).days)
    #print('day number', day_number_int)
    day_number_str = str(day_number_int)
    #print('day number string', day_number_str)


except Exception as e:
    print("Failure getting Trial info")
    print(str(e))

# Look specifically at phase data, as that carries the information on what the device should be doing
phaseData = t.phases

def main():
    
    try:
        s3 = boto3.resource('s3')

        list_of_files = glob.glob(IMAGE_DIR + '*')
        #print(list_of_files, 'list of files as an array')
        latest_file = max(list_of_files, key=os.path.getctime) #get the latest taken picture
        print('latest image selected for upload to S3: ', latest_file)
        data = open(latest_file, 'rb')
        name = os.path.basename(latest_file)
        s3_dir = (device_id + '/')
        s3_path = (s3_dir + name)
        print('path of upload in s3: ', s3_path)

        #If bucket was not public, we could also add credentials in here
        if trial_id_num != 0:
            s3.Bucket(S3_BUCKET).put_object(Key=name,
                                                           Body=data,
                                                           Metadata={'currTime':current_time,
                                                                     'device_id':device_id,
                                                                     'trial_id':trial_id,
								     'day_number':day_number_str,
                                                                    })
        else:
             s3.Bucket(S3_BUCKET).put_object(Key=name,
                                                           Body=data,
                                                           Metadata={'currTime':current_time,
                                                                     'device_id':device_id,
                                                                    })
        print('s3 upload COMPLETE - metadata sent... Current Time: ', current_time, ' Device ID: ', device_id, 'Trial ID: ', trial_id, 'Day Number: ', day_number_str)

    except Exception as e:
        print('S3 upload failed due to: ', e)

def test():
    main()
    print('Images pushed to s3.')

if __name__ == "__main__":
    test()
