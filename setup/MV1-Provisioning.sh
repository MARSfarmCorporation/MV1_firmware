#!/bin/bash

# Volume label of the USB stick or SD card
VOLUME_LABEL="PROVISION"

# Check if a serial number is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <serial_number>"
    exit 1
fi

SERIAL_NUMBER=$1
TARGET_PATH="/home/pi/Desktop/MV1_firmware/python/Sys_Conf.py"

# Find the mount point of the USB stick by its volume label
USB_BASE_PATH=$(findmnt -lno TARGET -S LABEL=$VOLUME_LABEL)

if [ -z "$USB_BASE_PATH" ]; then
    echo "USB stick with label $VOLUME_LABEL not found."
    exit 1
fi

# Path to the directory on the USB stick
DIR_ON_USB="${USB_BASE_PATH}/${SERIAL_NUMBER}"

# Path to the Sys_Conf.py file on the USB stick
FILE_ON_USB="${DIR_ON_USB}/Sys_Conf.py"

# Check if the Sys_Conf.py file exists in the USB directory
if [ -f "${FILE_ON_USB}" ]; then
    cp "${FILE_ON_USB}" "${TARGET_PATH}"
    echo "Sys_Conf.py has been replaced successfully."
else
    echo "No Sys_Conf.py found in ${DIR_ON_USB}"
fi
