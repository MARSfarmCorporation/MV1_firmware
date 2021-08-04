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
import datetime

def main():
    
    try:
        s3 = boto3.resource('s3')

        list_of_files = glob.glob('/home/pi/Desktop/MarsFarmMini/pictures/*')
        latest_file = max(list_of_files, key=os.path.getctime) #get the latest taken picture
        data = open(latest_file, 'rb')
        name = os.path.basename(latest_file)
        currTime = str(datetime.datetime.now())
        
        #If bucket was not public, we could also add credentials in here
        s3.Bucket('henry-metadata-testing').put_object(Key=name,
                                                       Body=data,
                                                       Metadata={'currTime':currTime,
                                                                 'device_id':'5678',
                                                                 'trial_id': '1234'
                                                                })
        
    except Exception as e:
        current_time = datetime.datetime.now()
        
        file = open('/home/pi/Desktop/MarsFarmMini/logs/S3.log', mode='a')
        file.write("%s : %s" % (current_time, str(e)))
        file.close()


if __name__ == "__main__":
    main()
    print('Images pushed to s3.')


