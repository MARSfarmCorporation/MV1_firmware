from datetime import datetime
from dateutil import parser
from Trial_Util import Trial
import json
import sqlite3

def devicedata_enqueue(mqtt_topic, name, value, unit, observation_date, model):
    t = Trial()
    date = parser.parse(datetime.fromtimestamp(observation_date).isoformat())
    day = abs((datetime.fromtimestamp(t.start_date) - datetime.fromtimestamp(observation_date)).days)
    week = abs(int(day / 7))
    formatted_date = datetime.fromtimestamp(observation_date).isoformat() + "Z"
    formatted_start = datetime.fromtimestamp(t.start_date).strftime("%Y-%m-%d %H:%M:%S")

    # setting the topic for the SQLite database entry
    topic = mqtt_topic

    # Creating the payload dictionary
    payload = {
        "timestamp": observation_date,
        "observation_date": formatted_date,
        "attribute": name,
        "value": value,
        "unit": unit,
        "trial_id": t.trial_id,
        "trial_name": t.trial_name,
        "trial_start_date": formatted_start,
        "day_number": day,
        "week_number": week,
        "model_name": model
    }
    # Convert the payload dictionary to a JSON string
    payload_json = json.dumps(payload)

    # Setting the status of the message to "Outbound - Unsent"
    status = "Outbound - Unsent"

    # Connecting to the SQLite database
    conn = sqlite3.connect('message_queue.db')
    cursor = conn.cursor()

    # Inserting the payload into the message_queue table
    cursor.execute("""
    INSERT INTO message_queue (topic, payload, status)
    VALUES (?, ?, ?)
    """, (topic, payload_json, status))

    conn.commit()
    conn.close()

