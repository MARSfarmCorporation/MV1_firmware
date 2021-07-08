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
MY_SPREADSHEET_ID = '1uyLUmLLBoTGfUO10SZthHJmspJTdniJ40CiSxPon_bs'
scopes = 'https://www.googleapis.com/auth/spreadsheets'

#Generate your own credential file to replace this
creds = ServiceAccountCredentials.from_json_keyfile_name('/home/pi/MVP/python/Marsfarm-SpreadSheet.json',scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(MY_SPREADSHEET_ID).sheet1

def update_sheet(observationType, datatype, value, unit):
    
    row = [str(datetime.datetime.now()), observationType, datatype,value,unit]
    sheet.insert_row(row)
    
def test():
    
    row = [str(datetime.datetime.now()), "ObservationType", 'Temperature','26','Celcius']
    sheet.insert_row(row)
    

if __name__ == '__main__':  
    test()
    