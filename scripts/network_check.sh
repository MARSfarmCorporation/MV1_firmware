#!/bin/bash

# Define a function to generate ISO 8601 formatted timestamp
timestamp() {
  date "+%Y-%m-%dT%H:%M:%SZ"
}

# Pings Google's IPv4 DNS Server one time with a timeout of 10 seconds to check for internet connectivity
if ping -4 -c 1 -W 10 google.com &> /dev/null; then
    exit 0
else
    echo "$(timestamp) ** Internet connection is down, restarting NetworkManager..."
    sudo systemctl restart NetworkManager

    # Wait a moment for NetworkManager to fully restart
    sleep 10

    # Reapply custom MAC addresses
    echo "Reapplying custom MAC addresses..."
    python3 /home/pi/Desktop/MV1_firmware/python/Ethernet.py
fi