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
CERTS_TARGET_PATH="/home/pi/certs"

# Directory to mount the USB stick
USB_MOUNT_DIR="/mnt/myusb"

# Find the device identifier of the USB stick by its volume label
USB_DEVICE="sda1"

# Mount the USB stick to the USB mount directory
if ! grep -qs "$USB_MOUNT_DIR" /proc/mounts; then
    sudo mkdir -p "$USB_MOUNT_DIR"
    sudo mount "/dev/$USB_DEVICE" "$USB_MOUNT_DIR"
fi

# Path to the directory on the USB stick
DIR_ON_USB="${USB_MOUNT_DIR}/${SERIAL_NUMBER}"

# Replace Sys_Conf.py file
FILE_ON_USB="${DIR_ON_USB}/Sys_Conf.py"
if [ -f "${FILE_ON_USB}" ]; then
    cp "${FILE_ON_USB}" "${TARGET_PATH}"
    echo "Sys_Conf.py has been replaced successfully."
else
    echo "No Sys_Conf.py found in ${DIR_ON_USB}"
fi

# Replace certificate files
declare -a CERT_FILES=("AmazonRootCA1.pem" "AmazonRootCA3.pem" "device.pem.crt.crt" "private.pem.key" "public.pem.key")

for cert_file in "${CERT_FILES[@]}"; do
    if [ -f "${DIR_ON_USB}/${cert_file}" ]; then
        cp "${DIR_ON_USB}/${cert_file}" "${CERTS_TARGET_PATH}/"
        echo "${cert_file} has been replaced successfully."
    else
        echo "No ${cert_file} found in ${DIR_ON_USB}"
    fi
done

# Optionally unmount the USB stick after the operation
sudo umount "$USB_MOUNT_DIR"
echo "USB stick has been unmounted successfully."
