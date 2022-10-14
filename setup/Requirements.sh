#!/bin/bash

#boto3 for Amazon S3 access
sudo pip3 install boto3

#awscli for AWS utility
sudo apt-get install awscli
#sudo pip3 install --upgrade awscli

#periphery for SI7021
sudo pip3 install python-periphery

#pyserial for MHZ16
sudo pip3 install pyserial

#multiple python libraries for google sheet
sudo pip3 install gspread
sudo pip3 install google-api-python-client
sudo pip3 install oauth2client

#New Requirements for GPIO actuation 
sudo apt-get install python3-pigpio
sudo apt-get install pigpio 
#apt-get install python-pigpio --- only needed if sensors still require Python 2 pigpio library

#New Requirements for MongoDB
sudo apt-get install python3-pymongo
sudo apt-get install python3-dnspython
#sudo pip3 install pymongo[srv]
sudo apt-get install python3-dotenv