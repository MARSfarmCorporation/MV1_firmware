'''
Responsible for connecting to google api and update google sheet

Owner: MARSfarm Corporation
Author: Jackie Zhong
Last Modified: 6/30/20
'''


from __future__ import print_function
import gspread
from googleapiclient.discovery import build  
from httplib2 import Http  
from oauth2client import file, client, tools  
from oauth2client.service_account import ServiceAccountCredentials  
import datetime

#change the spreadsheet ID to your own spreadsheet's
#MY_SPREADSHEET_ID = '1MbRqOJNc0r9TPLMbF1aurRuqOKW9dOkEYR2dR2dP5Ps'
MY_SPREADSHEET_ID = '1MbRqOJNc0r9TPLMbF1aurRuqOKW9dOkEYR2dR2dP5Ps'
scopes = 'https://www.googleapis.com/auth/spreadsheets'

#Generate your own credential file to replace this
creds = ServiceAccountCredentials.from_json_keyfile_name('/home/pi/MVP/python/Marsfarm-SpreadSheet.json',scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(MY_SPREADSHEET_ID).sheet1

def update_sheet(observationType, datatype, value, unit):
     
     date = (datetime.datetime.now() - datetime.datetime(1899, 12, 30))
     date_seconds = (date.total_seconds() / 86400)
     row = [date_seconds, observationType, datatype,value,unit]
     sheet.insert_row(row)
     
def test():
    test_date = (datetime.datetime.now() - datetime.datetime(1899, 12, 30))
    test_seconds = (test_date.total_seconds() / 86400)
    row = [test_seconds, "ObservationType", 'Temperature','26','Celcius']

if __name__ == '__main__':  
    test()
    