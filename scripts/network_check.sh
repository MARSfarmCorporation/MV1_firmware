#!/bin/bash

# Ping Google DNS to check for internet connectivity
if ping -4 -c 1 google.com &> /dev/null
then
    echo "Internet connection is up"
else
    echo "Internet connection is down, attempting to reconnect..."
    sudo systemctl restart NetworkManager
    # Wait a moment for NetworkManager to fully restart
    sleep 10
    # Reapply custom MAC addresses
    echo "Reapplying custom MAC addresses..."
    python3 /home/pi/Desktop/MV1_firmware/python/Ethernet.py
fi
