'''
This file was created to reassign a static MAC address to eth0 at boot, this was modeled after CameraAF.py
Previously this task was done entirely within cron, now though cron will call this python script so that variables may be kept within Sys_Conf.py
Author: Peter Webb - 04.05.2023

This file now also reassigns a static MAC address to wlan0 at boot
Updated By: Drew Thomas - 10.01.2023
'''
import os
#from time import sleep
#from Lights import Light
import datetime
from Sys_Conf import ETH_MAC_ADDRESS, WLAN_MAC_ADDRESS
from datetime import datetime

#time added for logging purposes
time = datetime.now().strftime("%Y-%m-%d_%H%M")

#last group of digits is the unit number within that batch
#second to last group of digits is the batch number
#third to last group of digits is the year

#cmd = ('sudo macchanger --mac=' + MAC_ADDRESS + ' eth0')
# Command to change the MAC address for eth0
cmd_eth = str('sudo macchanger --mac=' + ETH_MAC_ADDRESS + ' eth0')
print('Attempting to run command ', cmd_eth, ' at this time: ', time)
os.system(cmd_eth)

# Command to change the MAC address for wlan0
cmd_wlan = str('sudo macchanger --mac=' + WLAN_MAC_ADDRESS + ' wlan0')
print('Attempting to run command ', cmd_wlan, ' at this time: ', time)
os.system(cmd_wlan)

#flash lights red and blue to confirm ethernet connection
#lights = Light()
#lights.white()
#sleep(10)

#Return light to current setting
#import Light_Control
