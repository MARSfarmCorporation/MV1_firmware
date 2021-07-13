'''
Date: Jul 13, 2021
Author: Henry Borska (henryborska@wustl.edu)
'''
#Python version: 3.7.3
import csv
import collections
import pymongo
from pymongo import MongoClient
import time
import traceback
from dotenv import load_dotenv
load_dotenv()
import os
import sys
from bson import ObjectId 
from datetime import datetime 
from dateutil import parser
import math


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
        self.observation_date = self.formatDate(observation_date)
        self.attribute = attribute
        self.value = value
        self.unit = unit
        self.trial_id = ObjectId(trial_id)
        self.trial_name = trial_name
        self.day_number = self.calculateDayNum(trial_start_date, observation_date)
        self.week_number = self.calculateWeekNum(trial_start_date, observation_date)
        self.model_name = "EnvironmentalObservation"

    #Converting date from unix timestamp to datetime object with ISO format for Mongo
    def formatDate(self, unixDate):
        date = datetime.fromtimestamp(unixDate).isoformat()
        datetime_object = parser.parse(date)
        return datetime_object
    
    #Calculating the number of days and weeks from observation date and trial start date
    def calculateDayNum(self, trialStartDate, observationDate):
        return math.ceil((observationDate - trialStartDate)/60/60/24)
    def calculateWeekNum(self, trialStartDate, observationDate):
        return math.ceil((observationDate - trialStartDate)/60/60/24/7)
        

# obs_to_add = EnvironmentalObservation(OBSERVATION_DATE, ATTRIBUTE, VALUE, UNIT, TRIAL_ID, TRIAL_NAME, TRIAL_START_DATE)

def insert_one(observation):
    collection.insert_one(observation.__dict__)

# if __name__ == '__main__':
#     insert_one(collection, obs_to_add)
#     print("Document Inserted!")

