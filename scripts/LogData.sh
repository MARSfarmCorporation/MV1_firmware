#!/bin/bash

timestamp="$(date +"%D %T")"
echo $(date +"%D %T") "Log Sensors"

#Log std JSON data
python3 /home/pi/Desktop/MarsFarmMini/python/LogSensors.py

