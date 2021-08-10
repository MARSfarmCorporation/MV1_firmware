from picamera import PiCamera
from time import sleep
import datetime
import os
import os
import glob
#import Lights
#import pigpio

#pi = pigpio.pi()

#lights = Lights.Light(26,5,6,13,19)

#Record previous light settings
#farred = pi.get_PWM_dutycycle(26)
#red = pi.get_PWM_dutycycle(5)
#green = pi.get_PWM_dutycycle(6)
#blue = pi.get_PWM_dutycycle(13)
#white = pi.get_PWM_dutycycle(19)

#Turn off light
#lights.customMode(0,0,0,0,0)

#Set camera resolution
camera = PiCamera(resolution=(1920,1080))
camera.rotation = 180 # uncomment if picture is upside down
# Set focus
low = 0 # Lowest focal value
high = 1000 # Highest focal value
for i in range(low/10,(high+1)/10):
	focus =  i*10 #6 to 14 inches
	value = (focus<<4) & 0x3ff0
	dat1 = (value>>8)&0x3f
	dat2 = value & 0xf0
	os.system("i2cset -y 0 0x0c %d %d" % (dat1,dat2))

	#Turn on white light at 50%
	#lights.customMode(0,0,0,0,127)

	#Take picture
	sleep(2)
	camera.capture('/home/pi/Desktop/MarsFarmMini/pictures/' + str(focus) + '.jpg')

camera.close()

#Return light to previous settings
#lights.customMode(farred,red,green,blue,white)

