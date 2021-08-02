from picamera import PiCamera
from time import sleep
import datetime
import os
import os
import glob

#Clear previous photos from directory to prevent SD card from becoming full
files = glob.glob('/home/pi/Desktop/MarsFarmMini/pictures/*.jpg')

for f in files:
    try:
        f.unlink() #Delete file in list
    except OSError as e:
        print("Error: %s : %s" % (f, e.strerror))#Throw error
        
#Set camera resolution
camera = PiCamera(resolution=(1080,720))
#camera.rotation = 180 # uncomment if picture is upside down
# Set focus
focus =  50 #6 to 14 inches
value = (focus<<4) & 0x3ff0
dat1 = (value>>8)&0x3f
dat2 = value & 0xf0
os.system("i2cset -y 0 0x0c %d %d" % (dat1,dat2))

sleep(2)
camera.capture('/home/pi/Desktop/MarsFarmMini/pictures/' + format(datetime.datetime.now(), '%Y-%m-%d_%H%M') + '.jpg')
camera.close()
