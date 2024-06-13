import psutil
import subprocess
import socket
import datetime
import json
from Sys_Conf import DEVICE_ID
from WebSocketUtil import secure_database_write

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
        result = subprocess.run(['iwgetid', '-r', interface], capture_output=True, text=True)
        ssid = result.stdout.strip()
        if ssid:
            return ssid
        else:
            return 'No SSID found'
    except subprocess.CalledProcessError:
        return 'Error getting SSID'

def main():
    interface = get_connection_method()
    if interface != 'None':
        ip_address = get_ip_address(interface)
        ssid = get_ssid(interface) if interface == 'wlan0' else 'Not applicable'
        
        # Write the network information to the database to send to the MongoDB device record
        topic = f"network-info/{DEVICE_ID}"
        payload = {
            "timestamp": datetime.datetime.now().timestamp(),
            "connection_method": interface,
            "ip_address": ip_address,
            "ssid": ssid
        }
        payload_json = json.dumps(payload)
        status = "Outbound - Unsent"
        try:
            secure_database_write(topic, payload_json, status)
        except Exception as e:
            print(f"Error logging network data: {e}")
    else:
        print("No network connection detected")

if __name__ == "__main__":
    main()
