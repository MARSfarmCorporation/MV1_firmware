'''
Responsible for connecting to google api and update google sheet

Owner: MARSfarm Corporation
Author: Jackie Zhong - 6/30/20
Modified By: Peter Webb -  10/30/21
Modified By: Peter Webb -  11/10/22
'''


from __future__ import print_function
import gspread
from googleapiclient.discovery import build  
from httplib2 import Http  
from oauth2client import file, client, tools  
from oauth2client.service_account import ServiceAccountCredentials  
import datetime
from Sys_Conf import GOOGLE_SHEET_ID, DEVICE_ID

#change the spreadsheet ID to your own spreadsheet's
MY_SPREADSHEET_ID = GOOGLE_SHEET_ID
scopes = 'https://www.googleapis.com/auth/spreadsheets'

#Generate your own credential file to replace this
creds = ServiceAccountCredentials.from_json_keyfile_name('/home/pi/Desktop/MV1_firmware/python/Marsfarm-SpreadSheet.json',scopes)
client = gspread.authorize(creds)

# open the first sheet of the specified spreadsheet
sheet = client.open_by_key(MY_SPREADSHEET_ID).sheet1
#sheet = client.open_by_key(MY_SPREADSHEET_ID).device

# define a function to update the google sheet
def update_sheet(observationType, datatype, value, unit):
     # calculate the current date and time 
     date = (datetime.datetime.now() - datetime.datetime(1899, 12, 30))
     date_seconds = (date.total_seconds() / 86400)

     row = [date_seconds, observationType, datatype,value,unit,DEVICE_ID] # create a row of data to insert into the sheet
     sheet.insert_row(row) # insert the row into the sheet 
    
# define a test function to demonstrate updating the sheet 
def test():
    test_date = (datetime.datetime.now() - datetime.datetime(1899, 12, 30))
    test_seconds = (test_date.total_seconds() / 86400)
    row = [test_seconds, "ObservationType", 'Temperature','26','Celcius']
    sheet.insert_row(row)

if __name__ == '__main__':  
    test()
    
