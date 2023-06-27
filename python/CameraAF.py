'''
Function to set lights and take an image using Arducam Autofocus 16 MB IMX519 Camera
Author: Tyler Richards - 08.10.2020
Modified By: Howard Webb - 11/2/2022
'''
import libcamera
from time import sleep
from datetime import datetime
import os
import glob
from Sys_Conf import IMAGE_DIR
from Lights import Light

# Retrieve the current time for logging purposes
time = datetime.now().strftime("%Y-%m-%d_%H%M")

# set light to white for taking image
lights = Light() 
lights.white()
sleep(2)

#Take picture
file_name = time + '.jpg' # construct the file name using the current time 
print('image will be saved to: ', IMAGE_DIR + file_name) 
cmd = '/usr/local/bin/libcamera-still -t 5000 --nopreview --width 1920 --height 1080 --continue-autofocus -o {}'.format(IMAGE_DIR + file_name)
# construct the commad to capture the image using the libcamera-still command-line utility 
os.system(cmd)

#Return light to current setting
import Light_Control