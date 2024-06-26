'''
This file was created to reassign a static MAC address to eth0 at boot, this was modeled after CameraAF.py
Previously this task was done entirely within cron, now though cron will call this python script so that variables may be kept within Sys_Conf.py
Author: Peter Webb - 04.05.2023

This file now also reassigns a static MAC address to wlan0 at boot
Updated By: Drew Thomas - 10.01.2023

This file now also brings down the interface and then back up to ensure the MAC address is changed. Upon failure, it will also blink the lights blue
'''


import subprocess
import datetime
from Sys_Conf import ETH_MAC_ADDRESS, WLAN_MAC_ADDRESS
from Lights import Light

# Function to get the current MAC address of a given interface
def get_current_mac(interface):
    try:
        # First, get interface details
        result = subprocess.run(['ip', 'link', 'show', interface], check=True, stdout=subprocess.PIPE)
        output = result.stdout.decode()

        # Now, process the output in Python to find the MAC address
        for line in output.split('\n'):
            if 'link/ether' in line:
                mac_address = line.split()[1]
                return mac_address
    except subprocess.CalledProcessError as e:
        print(f"Failed to get MAC address for {interface}: {e}")
        return None

# Function to change the MAC address of a given interface
def change_mac(interface, desired_mac_address):
    current_mac = get_current_mac(interface)
    if current_mac == desired_mac_address:
        print(f"{interface} already has the desired MAC address {desired_mac_address}.")
        return

    # Take down the interface
    subprocess.run(['sudo', 'ifconfig', interface, 'down'])

    try:
        # Change the MAC address
        cmd = f'sudo macchanger --mac={desired_mac_address} {interface}'
        subprocess.run(cmd.split(), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f'Success: Changed MAC for {interface} at {datetime.datetime.now()}')
    except subprocess.CalledProcessError as e:
        print(f'Error: Failed to change MAC for {interface} at {datetime.datetime.now()} - {e.stderr.decode()}')
        light = Light()
        light.mac_fail()  # Call the mac_fail function from Light class
    finally:
        # Bring up the interface regardless of previous success or failure
        subprocess.run(['sudo', 'ifconfig', interface, 'up'])

# Instantiate the Light class
light = Light()

# Change MAC addresses
change_mac('eth0', ETH_MAC_ADDRESS)
change_mac('wlan0', WLAN_MAC_ADDRESS)

#Return light to current setting
import Light_Control
