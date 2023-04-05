'''
This file was created to reassign a static MAC address to eth0 at boot, this was modeled after CameraAF.py
Previously this task was done entirely within cron, now though cron will call this python script so that variables may be kept within Sys_Conf.py
Author: Peter Webb - 04.05.2023
'''
import os
#from time import sleep
#from Lights import Light
import datetime
from Sys_Conf import MAC_ADDRESS
from datetime import datetime

#time added for logging purposes
time = datetime.now().strftime("%Y-%m-%d_%H%M")

#last group of digits is the unit number within that batch
#second to last group of digits is the batch number
#third to last group of digits is the year

#cmd = ('sudo macchanger --mac=' + MAC_ADDRESS + ' eth0')
cmd = str('sudo macchanger --mac='+MAC_ADDRESS+' eth0')
print('Attempting to run command ', cmd, ' at this time: ', time)
os.system(cmd)

#flash lights red and blue to confirm ethernet connection
#lights = Light()
#lights.white()
#sleep(10)

#Return light to current setting
#import Light_Control
