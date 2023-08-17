'''
Controller function for the pump class
Author: Tyler Richards - 05.10.2022
Modified By: Howard Webb - 11/2/2022
'''
from Trial_Util import Trial
from Pump import Pump
from datetime import datetime
from WebSocketUtil import enqueue
import sqlite3

# Import dictionary data
t = Trial()

# Get current time
time = datetime.now().strftime("%y-%m-%d %H:%M:%S")
observation_date = datetime.now().timestamp()

# creating an instance of the pump class
p = Pump()

# check to verify that pump is not already pumping to prevent overwrite
if p.is_pumping():
   print('Pump is already Pumping')
   exit

# retrieve pump settings from trial
ps = t.get_pump_setting()

p.dispense(ps) # dispensing specified amount of water
if (ps > 0):

    # Creating the payload via the enqueue function
    payload = enqueue("pump", ps, "mL", observation_date, "PumpObservation")

    # Connecting to the SQLite database
    conn = sqlite3.connect('message_queue.db')
    cursor = conn.cursor()

    # Inserting the payload into the message_queue table
    cursor.execute("""
    INSERT INTO message_queue (topic, payload, status)
    VALUES (?, ?, ?)
    """, ("devicedata", payload, "Outbound - Unsent"))

    conn.commit()
    conn.close()

print('Pump dispersed ', ps, ' ML of water on ', time)

def test_pump(amount):
    p = Pump()

    # Check to verify that pump is not already pumping to prevent overwrite
    if p.is_pumping():
        print('Pump is already Pumping')
        return

    # Get current time
    observation_date = datetime.now().timestamp()

    p.dispense(amount) # Dispensing specified amount of water

    if amount > 0:
        # Creating the payload via the enqueue function
        payload = enqueue("pump", amount, "mL", observation_date, "PumpObservation")

        # Connecting to the SQLite database
        conn = sqlite3.connect('message_queue.db')
        cursor = conn.cursor()

        # Inserting the payload into the message_queue table
        cursor.execute("""
        INSERT INTO message_queue (topic, payload, status)
        VALUES (?, ?, ?)
        """, ("devicedata", payload, "Outbound - Unsent"))

        conn.commit()
        conn.close()

    print('Test pump dispersed', amount, 'ML of water')
