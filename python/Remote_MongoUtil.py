'''
Date: Jul 13, 2021
Author: Henry Borska (henryborska@wustl.edu)
Modified By: Howard Webb 11.10.22
'''
#Python version: 3.7.3
#import csv
#import collections
import pymongo
from pymongo import MongoClient
#import time
#import traceback
#from dotenv import load_dotenv
#load_dotenv()
#import os
#import sys
from bson import ObjectId 
from datetime import datetime 
from dateutil import parser
import math
from Sys_Conf import MONGODB_RI, DB_NAME, COLLECTION_NAME

#Connecting pymongo to the proper collection in my database
MONGODB_URI = "mongodb+srv://device_data-RW:TOtuVtPoO8ePI5Ms@testing.7ppqd.mongodb.net/web-application?retryWrites=true&w=majority"
DB_NAME = "web-application"
COLLECTION_NAME = "device-data"
# myClient = pymongo.MongoClient((os.environ.get("MONGODB_URI")))
myClient = pymongo.MongoClient(MONGODB_URI)
db = myClient[DB_NAME]
collection = db[COLLECTION_NAME] #which collection to add to


#Defining a class for an Environmental Observation to insert
class EnvironmentalObservation(object):
    def __init__(self, observation_date, attribute, value, unit, trial_id, trial_name, trial_start_date):
        # observation_date as timestamp
        # attribute string
        # value normally integer
        # unit string
        # trial_id is string
        # trial_name is string
        # trial_start_date as timestamp
        
        #self.observation_date = self.formatDate(observation_date)
        self.timestamp = observation_date
        self.observation_date = self.formatDate(observation_date)
        self.attribute = attribute
        self.value = value
        self.unit = unit
        self.trial_id = ObjectId(trial_id)
        #self.trial_id = trial_id
        self.trial_name = trial_name
        self.trial_start_date = self.formatDate(trial_start_date)
        #self.trial_start_date = trial_start_date
        self.day_number = self.calculateDayNum(trial_start_date, observation_date)
        self.week_number = self.calculateWeekNum(self.day_number)
        self.model_name = "EnvironmentalObservation"

    #Converting date from unix timestamp to datetime object with ISO format for Mongo
    def formatDate(self, timestamp):
        date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        #datetime_object = parser.parse(date)
        return date
    
    def calculateDayNum(self, start_timestamp, observation_timestamp):
        # Calculate day of trial - assume base 0
        sd = datetime.fromtimestamp(start_timestamp)
        od = datetime.fromtimestamp(observation_timestamp)
        return (sd - od).days       

    def calculateWeekNum(self, days):
        # Calculate week of trial - assume base 0
        return int(days/7)

# obs_to_add = EnvironmentalObservation(OBSERVATION_DATE, ATTRIBUTE, VALUE, UNIT, TRIAL_ID, TRIAL_NAME, TRIAL_START_DATE)

def insert_one(observation):
    collection.insert_one(observation.__dict__)

def test():
    from Trial_Util import Trial
    t = Trial()
    # observation_date assume to be datetime object
    #od = datetime.now().timestamp()
    d = datetime.now()
    print(d)
    od = d.timestamp()
    print(od)
    
    print(od)
    # attribute string
    attr = "Temperature"
    # value normally integer
    value = 32
    # unit string
    unit = "C"
    # trial_id is string
    trial_id = t.trial_id
    # trial_name is string
    trial_name = t.trial_name
     # trial_start_date as timestamp
    sd = t.start_date
    e = EnvironmentalObservation(od, attr, value, unit, trial_id, trial_name, sd)
    print(e.__dict__)

if __name__=='__main__':
     test()
#     insert_one(collection, obs_to_add)
#     print("Document Inserted!")