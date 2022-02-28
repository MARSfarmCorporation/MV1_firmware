#Start pigpio service
import os
import time
os.system('sudo pigpiod -s1')
time.sleep(1) #wait to execute
