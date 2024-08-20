#!/bin/bash

echo "Starting IPv6 disable process..."

# Backup the current sysctl.conf file
sudo cp /etc/sysctl.conf /etc/sysctl.conf.backup

# Remove any existing lines that disable IPv6 to avoid duplication
sudo sed -i '/net.ipv6.conf.all.disable_ipv6/d' /etc/sysctl.conf
sudo sed -i '/net.ipv6.conf.default.disable_ipv6/d' /etc/sysctl.conf

# Add the lines to disable IPv6
echo 'net.ipv6.conf.all.disable_ipv6 = 1' | sudo tee -a /etc/sysctl.conf
echo 'net.ipv6.conf.default.disable_ipv6 = 1' | sudo tee -a /etc/sysctl.conf

# Apply the changes
sudo sysctl -p

echo "IPv6 has been disabled successfully."
