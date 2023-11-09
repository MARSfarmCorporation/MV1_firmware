from datetime import datetime
from dateutil import parser
from Trial_Util import Trial
import json
import sqlite3
import threading
from Sys_Conf import SERIAL_NUMBER

# Create a thread lock for the database
database_lock = threading.Lock()

###########################################################################################################################
# COMMON FUNCTIONS FOR DATABASE CONNECTIONS
###########################################################################################################################

# This function uses thread locking to ensure that only one thread can write to the database at a time
def secure_database_write(topic, payload_json, status):
    print("Attempting to acquire database lock...")
    with database_lock:
        print("Database lock acquired.")
        
        try:
            # Connecting to the SQLite database
            print("Connecting to SQLite database...")
            conn = sqlite3.connect('/home/pi/Desktop/MV1_firmware/python/message_queue.db')
            conn.execute("PRAGMA busy_timeout = 2000")  # Setting a busy timeout of 2000 milliseconds
            cursor = conn.cursor()
            print("Successfully connected to SQLite database.")

            # Inserting the payload into the message_queue table
            print("Inserting data into message_queue table...")
            cursor.execute("""
            INSERT INTO message_queue (topic, payload, status)
            VALUES (?, ?, ?)
            """, (topic, payload_json, status))
            print("Data successfully inserted.")

            # Committing the transaction
            print("Committing the transaction...")
            conn.commit()
            print("Transaction committed.")
        
        except sqlite3.Error as e:
            print(f"SQLite error occurred: {e}")
        
        finally:
            # Closing the database connection
            print("Closing the database connection...")
            conn.close()
            print("Database connection closed.")
            
        print("Releasing database lock...")
    print("Database lock released.")


# This function uses thread locking to ensure that only one thread can update the database at a time
def secure_database_update(id, status):
    with database_lock:
        try:
            with open('../logs/Broker_Log.txt', 'a') as file:
                file.write(f"WebSocketUtils.py: Attempting to change status of: {id}\n")
            # Connecting to the SQLite database
            conn = sqlite3.connect('/home/pi/Desktop/MV1_firmware/python/message_queue.db')
            conn.execute("PRAGMA busy_timeout = 2000")  # Setting a busy timeout of 2000 milliseconds
            cursor = conn.cursor()

            # Updating the status in the message_queue table
            cursor.execute("""
            UPDATE message_queue
            SET status = ?
            WHERE id = ?
            """, (status, id))

            # Committing the transaction
            conn.commit()
        
        except sqlite3.Error as e:
            print(f"SQLite error occurred: {e}")
            with open('../logs/Broker_Log.txt', 'a') as file:
                file.write(f"WebSocketUtils.py: Database status update: {e}\n")
        
        finally:
            # Closing the database connection
            conn.close()

# This function is used to write a new record to the database with a specific id
def secure_database_write_with_id(id, topic, payload, status):
    with database_lock:
        try:
            # Connecting to the SQLite database
            conn = sqlite3.connect('/home/pi/Desktop/MV1_firmware/python/message_queue.db')
            conn.execute("PRAGMA busy_timeout = 2000")  # Setting a busy timeout of 2000 milliseconds
            cursor = conn.cursor()

            # Update the record if it exists, otherwise insert it
            cursor.execute("""
            INSERT INTO message_queue (id, topic, payload, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
            topic=excluded.topic,
            payload=excluded.payload,
            status=excluded.status
            """, (id, topic, payload, status))

            # Committing the transaction
            conn.commit()
        
        except sqlite3.Error as e:
            print(f"SQLite error occurred: {e}")
        
        finally:
            # Closing the database connection
            conn.close()


###########################################################################################################################
# DATA LOGGING
###########################################################################################################################

# This function logs data to be sent to the MongoDB database via the message_queue.db route
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
    try:
        secure_database_write(topic, payload_json, status)
    except Exception as e:
        print(f"Error logging device data: {e}")

# This function logs data to be sent to the AWS IoT Core via the message_queue.db route
def aws_enqueue(mqtt_topic, mqtt_payload):
    # setting the topic for the SQLite database entry
    topic = mqtt_topic

    # Convert the payload dictionary to a JSON string
    payload_json = json.dumps(mqtt_payload)

    # Setting the status of the message to "Outbound - Unsent"
    status = "Outbound - Unsent"

    # Connecting to the SQLite database
    try:
        secure_database_write(topic, payload_json, status)
    except Exception as e:
        print(f"Error logging device data: {e}")
        with open('../logs/Job_Agent_Log.txt', 'a') as file:
            file.write(f"WebSocketUtil.py: Failed to enqueue: {e}\n")

###########################################################################################################################
# ERROR LOGGING
###########################################################################################################################

# This function logs a failed job process and the return code of the job_agent script to the 'logs/job_fail/{thing_name}' topic when called by the broker.
def log_job_fail(return_code):
    try:
        # Setting up the message
        topic = "log/job_fail/" + SERIAL_NUMBER
        message_payload = {
            "timestamp": datetime.now().timestamp(),
            "return_code": return_code
        }
        payload_json = json.dumps(message_payload)
        status = "Outbound - Unsent"

        # Use the secure_database_connection function to insert the data
        secure_database_write(topic, payload_json, status)

    except Exception as e:
        print(f"Error logging job failure: {e}")
