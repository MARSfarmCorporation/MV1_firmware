import psutil
import subprocess
import socket
import datetime
import json
from Sys_Conf import DEVICE_ID
from WebSocketUtil import secure_database_write
from version import firmware_version

def get_connection_method():
    interfaces = psutil.net_if_addrs()
    for interface in interfaces:
        if 'eth0' in interface:
            return 'eth0'
        elif 'wlan0' in interface:
            return 'wlan0'
    return 'None'

def get_ip_address(interface):
    addresses = psutil.net_if_addrs().get(interface, [])
    for address in addresses:
        if address.family == socket.AF_INET:
            return address.address
    return 'No IP found'

def get_ssid(interface):
    try:
        result = subprocess.run(['/usr/sbin/iwgetid', '-r', interface], capture_output=True, text=True)
        ssid = result.stdout.strip()
        if ssid:
            return ssid
        else:
            return 'No SSID found'
    except subprocess.CalledProcessError:
        return 'Error getting SSID'

def get_visible_ssids(interface):
    try:
        result = subprocess.run(['sudo', '/usr/sbin/iwlist', interface, 'scan'], capture_output=True, text=True)
        output = result.stdout.split('\n')
        ssids = []
        for line in output:
            if "ESSID" in line:
                ssid = line.split(':')[1].strip().strip('"')
                if ssid:
                    ssids.append(ssid)
        return ssids if ssids else ['No SSIDs found']
    except subprocess.CalledProcessError:
        return ['Error scanning for SSIDs']

def main():
    interface = get_connection_method()
    if interface != 'None':
        ip_address = get_ip_address(interface)
        ssid = get_ssid(interface) if interface == 'wlan0' else 'Not applicable'
        visible_ssids = get_visible_ssids(interface) if interface == 'wlan0' else ['Not applicable']
        
        # Write the network information and firmware version to the database to send to the MongoDB device record
        topic = f"device-report/{DEVICE_ID}"
        payload = {
            "device_id": DEVICE_ID,
            "firmware_version": firmware_version,
            "network_info": {
                "timestamp": datetime.datetime.now().timestamp(),
                "connection_method": interface,
                "ip_address": ip_address,
                "connected_ssid": ssid,
                "visible_ssids": visible_ssids
            }
        }
        payload_json = json.dumps(payload)
        status = "Outbound - Unsent"
        try:
            print(f"Logging network data: {payload_json}")
            secure_database_write(topic, payload_json, status)
        except Exception as e:
            print(f"Error logging network data: {e}")
    else:
        print("No network connection detected")

if __name__ == "__main__":
    main()
