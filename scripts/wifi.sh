#!/usr/bin/env bash

export DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket

# Optional step - it takes couple of seconds (or longer) to establish a WiFi connection
# sometimes. In this case, following checks will fail and wifi-connect
# will be launched even if the device will be able to connect to a WiFi network.
# If this is your case, you can wait for a while and then check for the connection.
sleep 60

# Choose a condition for running WiFi Connect according to your use case:

# 1. Is there a default gateway?
# ip route | grep default

# 2. Is there Internet connectivity?
# nmcli -t g | grep full

# 3. Is there Internet connectivity via a google ping?
ping -4 -c 1 google.com

# 4. Is there an active WiFi connection?
# iwgetid -r

# check the exit code of the previous command (wget). If it's 0, the request was successful, indicating an internet connection.
if [ $? -eq 0 ]; then
    printf 'Skipping WiFi Connect\n'
else
    # if the exit code is not 0, start the wifi-connect service to establish a WiFi connection. 
    python3 /home/pi/Desktop/MV1_firmware/python/WiFiConnectIndicator.py
    printf 'Starting WiFi Connect\n'
    #sudo wifi-connect
fi

# Start your application here.
sleep infinity
