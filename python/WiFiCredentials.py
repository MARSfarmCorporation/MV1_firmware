import os
import shutil
import subprocess
from Lights import Light

# Attempt to mount a USB drive and process a file with WiFi credentials

# Paths and filenames
MOUNT_POINT = '/mnt/usb'
TARGET_FILENAME = 'wifi_credentials.txt'
PROCESSING_DIR = '/home/pi/'  # Directory where the file will be processed

def mount_usb():
    result = subprocess.run(['sudo', 'mount', '/dev/sda1', MOUNT_POINT], capture_output=True, text=True)
    return result.returncode == 0

def unmount_usb():
    result = subprocess.run(['sudo', 'umount', MOUNT_POINT], capture_output=True, text=True)
    return result.returncode == 0

def process_file(file_path):
    print(f'Processing file: {file_path}')
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
    return os.path.exists(config_path)

def add_wifi_credentials(ssid, password):
    config_content = f"""
[connection]
id={ssid}
uuid=$(uuidgen)
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
    
    if os.path.exists('/dev/sda1'):
        print('USB drive detected. Mounting...')
        if mount_usb():
            print('USB drive mounted.')
            for root, dirs, files in os.walk(MOUNT_POINT):
                if TARGET_FILENAME in files:
                    file_path = os.path.join(root, TARGET_FILENAME)
                    process_file(file_path)
                    break
            unmount_usb()
            print('USB drive unmounted.')

            light = Light()
            light.wifi_credentials_success()

            import Light_Control
        else:
            print('Failed to mount USB drive.')
            light = Light()
            light.wifi_credentials_fail()

            import Light_Control
    else:
        exit(0)

if __name__ == "__main__":
    main()
