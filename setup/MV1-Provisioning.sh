#!/bin/bash

# Volume label of the USB stick
VOLUME_LABEL="Provision"

# Check if a serial number is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <serial_number>"
    exit 1
fi

SERIAL_NUMBER=$1
TARGET_PATH="/home/pi/Desktop/MV1_firmware/python/Sys_Conf.py"

# Directory to mount the USB stick
USB_MOUNT_DIR="/mnt/myusb"

# Find the device identifier of the USB stick by its volume label
USB_DEVICE=$(lsblk -no NAME,LABEL | grep $VOLUME_LABEL | awk '{print $1}')

if [ -z "$USB_DEVICE" ]; then
    echo "USB stick with label $VOLUME_LABEL not found."
    exit 1
fi

# Mount the USB stick to the USB mount directory
if ! grep -qs "$USB_MOUNT_DIR" /proc/mounts; then
    sudo mkdir -p "$USB_MOUNT_DIR"
    sudo mount "/dev/$USB_DEVICE" "$USB_MOUNT_DIR"
fi

# Path to the directory on the USB stick
DIR_ON_USB="${USB_MOUNT_DIR}/${SERIAL_NUMBER}"

# Path to the Sys_Conf.py file on the USB stick
FILE_ON_USB="${DIR_ON_USB}/Sys_Conf.py"

# Check if the Sys_Conf.py file exists in the USB directory
if [ -f "${FILE_ON_USB}" ]; then
    cp "${FILE_ON_USB}" "${TARGET_PATH}"
    echo "Sys_Conf.py has been replaced successfully."
else
    echo "No Sys_Conf.py found in ${DIR_ON_USB}"
fi

# Optionally unmount the USB stick after the operation
sudo umount "$USB_MOUNT_DIR"
echo "USB stick has been unmounted successfully."