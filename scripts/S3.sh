#!/bin/bash

#Telling the script where to find credentials
echo "locating config file for AWS upload"
AWS_CONFIG_FILE="~/.aws/config"

python3 ~/Desktop/MV1_firmware/python/S3.py
echo "image successfully uploaded to S3"