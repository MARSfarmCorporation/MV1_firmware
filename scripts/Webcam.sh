#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H%M")

fswebcam -r 640x360 --skip 10 --no-banner --set frequency=60 /home/pi/Desktop/MarsFarmMini/pictures/$DATE.jpg
