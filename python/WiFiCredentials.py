import os
import shutil
import json
import subprocess
from Lights import Light

# Attempt to mount a USB drive and process a file with WiFi credentials

# Paths and filenames
MOUNT_POINT = '/mnt/usb'
TARGET_FILENAME = 'wifi_credentials.txt'
PROCESSING_DIR = '/home/pi/'  # Directory where the file will be processed

def get_usb_devices():
    result = subprocess.run(['lsblk', '-o', 'NAME,MOUNTPOINT,TYPE', '-J'], capture_output=True, text=True)
    devices = []
    if result.returncode == 0:
        output = json.loads(result.stdout)
        for device in output['blockdevices']:
            if device['mountpoint'] is None and device['name'].startswith('sd'):
                if device['type'] == 'disk':
                    # Include whole devices (e.g., /dev/sda)
                    devices.append(device['name'])
                if 'children' in device:
                    # Include partitions (e.g., /dev/sda1)
                    for child in device['children']:
                        devices.append(child['name'])
    return devices

def mount_usb(device):
    device_path = f'/dev/{device}'
    result = subprocess.run(['sudo', 'mount', device_path, MOUNT_POINT], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to mount {device_path}: {result.stderr}")  # Debug print
    return result.returncode == 0

def unmount_usb():
    result = subprocess.run(['sudo', 'umount', MOUNT_POINT], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to unmount {MOUNT_POINT}: {result.stderr}")  # Debug print
    return result.returncode == 0

def process_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    if len(lines) >= 2:
        ssid = lines[0].strip()
        password = lines[1].strip()
        if not wifi_credential_exists(ssid):
            add_wifi_credentials(ssid, password)
    shutil.move(file_path, os.path.join(PROCESSING_DIR, os.path.basename(file_path)))

def wifi_credential_exists(ssid):
    config_path = f"/etc/NetworkManager/system-connections/{ssid}.nmconnection"
    exists = os.path.exists(config_path)
    return exists

def add_wifi_credentials(ssid, password):
    config_content = f"""
[connection]
id={ssid}
interface-name=wlan0
type=wifi

[wifi]
mode=infrastructure
ssid={ssid}

[wifi-security]
key-mgmt=wpa-psk
psk={password}

[ipv4]
dns-search=
method=auto

[ipv6]
addr-gen-mode=stable-privacy
dns-search=
method=auto
"""
    config_path = f"/etc/NetworkManager/system-connections/{ssid}.nmconnection"
    with open(config_path, 'w') as f:
        f.write(config_content)
    subprocess.run(['sudo', 'chmod', '600', config_path], capture_output=True, text=True)
    subprocess.run(['sudo', 'nmcli', 'connection', 'reload'], capture_output=True, text=True)
    subprocess.run(['sudo', 'nmcli', 'connection', 'up', ssid], capture_output=True, text=True)
    print(f'Added and activated WiFi connection for SSID: {ssid}')

def main():
    if not os.path.exists(MOUNT_POINT):
        os.makedirs(MOUNT_POINT)
    
    usb_devices = get_usb_devices()
    if usb_devices:
        for device in usb_devices:
            if mount_usb(device):
                for root, dirs, files in os.walk(MOUNT_POINT):
                    if TARGET_FILENAME in files:
                        file_path = os.path.join(root, TARGET_FILENAME)
                        process_file(file_path)

                        light = Light()
                        light.wifi_credentials_success()

                        import Light_Control

                        break

                unmount_usb()
            else:
                print(f'Failed to mount USB drive: {device}.')

                light = Light()
                light.wifi_credentials_fail()

                import Light_Control
    else:
        exit(0)

if __name__ == "__main__":
    main()
