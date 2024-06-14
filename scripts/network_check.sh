#!/bin/bash

# Path to the counter file
COUNTER_FILE="/home/pi/.wifi_connect_counter"

# Define a function to generate ISO 8601 formatted timestamp
timestamp() {
  date "+%Y-%m-%dT%H:%M:%SZ"
}

# Initialize counter if not present
if [ ! -f "$COUNTER_FILE" ]; then
  echo 0 > "$COUNTER_FILE"
fi

# Read the current counter value
COUNTER=$(cat "$COUNTER_FILE")

# Check if wifi-connect is active by checking the IP address of wlan0
if ip addr show wlan0 | grep -q "192.168.42.1"; then
  # Increment the counter
  COUNTER=$((COUNTER + 1))
  echo "$COUNTER" > "$COUNTER_FILE"

  # If the counter is less than 5 (25 minutes with a 5-minute interval), exit the script
  if [ "$COUNTER" -lt 5 ]; then
    echo "$(timestamp) ** wifi-connect is active, counter at $COUNTER, skipping NetworkManager restart..."
    exit 0
  fi
else
  # Reset the counter if wifi-connect is not active
  COUNTER=0
  echo "$COUNTER" > "$COUNTER_FILE"
fi

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
