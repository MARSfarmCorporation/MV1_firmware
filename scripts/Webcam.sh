#!/bin/bash
#python3 /home/pi/Desktop/MarsFarmMini/python/CameraAF.py
DATE=$(date +"%Y-%m-%d_%H%M")
#takes a 4 MG photo using autofocus for five seconds and then saves it locally
libcamera-still -t 5000 --viewfinder-width 2328 --viewfinder-height 1748 --autofocus -o /home/pi/Desktop/MV1_firmware/pictures/$DATE.jpg