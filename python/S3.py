'''
    Created 6/11/20
    
    Responsible for connecting to and uploading image to Amazon S3
    
    Owner: MARSfarm Corporation
    Author: Jackie Zhong(zy99120@gmail.com), Henry Borska(henryborska@wustl.edu)
    Last Modified: 8/4/21
'''

import glob
import os
import boto3
from Trial_Util import Trial
import time
from datetime import datetime
from Sys_Conf import IMAGE_DIR, S3_BUCKET

current_time = datetime.now().strftime('%Y-%m-%d_%H%M')
print('Attempting S3 connection at: ', current_time)
# Try to get device ID and trial ID from JSON
try:
    t = Trial()
    trial_id_num = t.trial_id
    trial_id = str(t.trial_id)
    device_id = str(t.device_id)
    
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

        #If bucket was not public, we could also add credentials in here
        if trial_id_num != 0:
            s3.Bucket(S3_BUCKET).put_object(Key=name,
                                                           Body=data,
                                                           Metadata={'currTime':current_time,
                                                                     'device_id':device_id,
                                                                     'trial_id':trial_id
                                                                    })
        else:
             s3.Bucket(S3_BUCKET).put_object(Key=name,
                                                           Body=data,
                                                           Metadata={'currTime':current_time,
                                                                     'device_id':device_id,
                                                                    })
        
    except Exception as e:
        print(e)
        print('Images pushed to S3.')


if __name__ == "__main__":
    main()
    #print('Images pushed to s3.')


