#!/bin/sh

# Load configuration to cron
# Author: Howard Webb
# Date: 11/16/2017
# Modified locally by PW - 11.07.2022

# script to load cron job file

timestamp="$(date +"%D %T")"

crontab ~/Desktop/MV1_firmware/setup/MV1_firmware_cron.txt
echo $(date +"%D %T") "Cron loaded"