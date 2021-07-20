#!/bin/bash

#fswebcam for picture taking
sudo apt install fswebcam

#boto3 for Amazon S3 access
sudo pip3 install boto3

#awscli for AWS utility
sudo apt install awscli
sudo pip3 install --upgrade awscli

#periphery for SI7021
sudo pip3 install python-periphery

#pyserial for MHZ16
sudo pip3 install pyserial

#multiple python libraries for google sheet
sudo pip3 install gspread
sudo pip3 install google-api-python-client
sudo pip3 install oauth2client

#New Requirements for GPIO actuation 
sudo apt-get install pigpio python-pigpio python3-pigpio

#New Requirements for MongoDB
pip3 install pymongo
pip3 install pymongo[srv]
pip3 install python-dotenv

