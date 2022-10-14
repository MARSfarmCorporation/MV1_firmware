import libcamera
from time import sleep
import datetime
import os
import glob
import Lights
import pigpio

pi = pigpio.pi()

lights = Lights.Light(26,5,13,19)

#Record previous light settings
farred = pi.get_PWM_dutycycle(26)
red = pi.get_PWM_dutycycle(5)
blue = pi.get_PWM_dutycycle(13)
white = pi.get_PWM_dutycycle(19)

#Turn off light
lights.customMode(0,0,0,0)

#Clear previous photos from directory to prevent SD card from becoming full
files = glob.glob('/home/pi/Desktop/MarsFarmMini/pictures/*.jpg')

for f in files:
    try:
        os.remove(f) #Delete file in list
    except OSError as e:
        print("Error: %s : %s" % (f, e.strerror))#Throw error

#Turn on white light at 50%
lights.customMode(0,0,0,255)

#Take picture
sleep(2)

###### libcamera script will go here ########

camera.capture('/home/pi/Desktop/MarsFarmMini/pictures/' + format(datetime.datetime.now(), '%Y-%m-%d_%H%M') + '.jpg')
camera.close()

#Return light to previous settings
lights.customMode(farred,red,blue,white)
