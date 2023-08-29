#!/bin/bash

echo "Attemping to pull GitHub"
cd /home/pi/Desktop/MV1_firmware
git pull
echo "Pulled GitHub successfully"
cd setup
crontab MV1_firmware_crontab.txt
echo "Updated crontab successfully"

