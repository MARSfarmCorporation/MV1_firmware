import sqlite3
import time
import json
import socket
import subprocess
from Sys_Conf import DEVICE_ID, SERIAL_NUMBER
from WebSocketUtil import log_job_fail, secure_database_update

###########################################################################################################################
# DEFINE TOPICS
###########################################################################################################################

trial_topic = 'trial/' + DEVICE_ID
job_notify_topic = f'$aws/things/{SERIAL_NUMBER}/jobs/notify-next'

###########################################################################################################################
# SPECIAL HANDLER FUNCTIONS
###########################################################################################################################

def spawn_job_agent(id, payload):
    try:
        # write the payload to Job_Agent_Log.txt, on a new line each time (make sure the file is there), with the prefix "Broker.py: "
        #with open('Job_Agent_Log.txt', 'a') as file:
        #    file.write(f"Broker.py: {payload}\n")

        # Start the Job_Agent.py process and pass the payload
        result = subprocess.run(['python3', 'Job_Agent.py', payload],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                timeout=30)

        # Check the return code to determine the status. Log the return code to the job_fail topic if the job fails.
        if result.returncode == 0:
            status = 'Inbound - Sorted'
            secure_database_update(id, status)
        else:
            return_code = result.returncode
            log_job_fail(return_code)
            if result.returncode == 1:
                status = 'Inbound - Unsortable - Job Error 1'
                secure_database_update(id, status)
            elif result.returncode == 2:
                status = 'Inbound - Unsortable - Job Error 2'
                secure_database_update(id, status)
            elif result.returncode == 3:
                status = 'Inbound - Unsortable - Job Error 3'
                secure_database_update(id, status)
            else:
                status = 'Inbound - Unsortable - Job Error Unknown'
                secure_database_update(id, status)

    except subprocess.TimeoutExpired as e:
        print(f"Error executing the script: {e}")
        status = 'Inbound - Unsortable - Timeout'
        secure_database_update(id, status)
        #cursor.execute("UPDATE message_queue SET status = 'Inbound - Unsortable - Timeout' WHERE id = ?", (id,))

    except Exception as e:
        print(f"Error executing the script: {e}")
        status = 'Inbound - Unsortable - Unknown'
        secure_database_update(id, status)
        #cursor.execute("UPDATE message_queue SET status = 'Inbound - Unsortable - Unknown' WHERE id = ?", (id,))

# This function handles trial messages and writes them to trial.py. It then updates the status in the database.
def trial_handler(payload, id):
    try:
        # Write the payload to trial.py
        with open('trial.py', 'w') as file:
            file.write(payload)

        # Update the status in the database
        status = 'Inbound - Sorted'
        secure_database_update(id, status)
    except Exception as e:
        print(f"Error processing inbound message: {e}")
        status = 'Inbound - Unsortable - Unrecognized Topic'
        secure_database_update(id, status)

###########################################################################################################################
# INBOUND MESSAGE HANDLING
###########################################################################################################################

# This function handles inbound messages and sorts them via their topic. It then updates the status in the database.
def process_inbound_message(cursor, id, topic, payload):
    try:
        # Defined topics are handled here via their respective functions
        if topic == trial_topic:
            trial_handler(payload, id)
        if topic == job_notify_topic:
            spawn_job_agent(id, payload)
        else:
            # Handle other topics as needed
            pass
    except Exception as e:
        print(f"Error processing inbound message: {e}")
        status = 'Inbound - Unsortable - Unrecognized Topic'
        secure_database_update(id, status)
        #cursor.execute("UPDATE message_queue SET status = 'Inbound - Unsortable - Unrecognized Topic' WHERE id = ?", (id,))

###########################################################################################################################
# OUTBOUND MESSAGE HANDLING + SOCKET CLIENT
###########################################################################################################################

# This function handles outbound messages and sends them to the websocket server. It then updates the status in the database.
def process_outbound_message(cursor, id, topic, payload):
    try:
        # Create a Unix socket
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        
        # Connect to the Unix socket file
        client_socket.connect("/tmp/websocket_comms.sock")
        
        # Format the MQTT message
        message = json.dumps({"topic": topic, "payload": payload})
        
        # Send the message
        client_socket.sendall(message.encode())
        
        # Close the socket
        client_socket.close()
        
        # Update the status in the database
        status = 'Outbound - Sent'
        secure_database_update(id, status)
        #cursor.execute("UPDATE message_queue SET status = 'Outbound - Sent' WHERE id = ?", (id,))
    except Exception as e:
        print(f"Error sending outbound message: {e}")
        status = 'Outbound - Unsendable'
        secure_database_update(id, status)
        #cursor.execute("UPDATE message_queue SET status = 'Outbound - Unsendable' WHERE id = ?", (id,))

###########################################################################################################################
# MESSAGE_QUEUE.DB POLLING
###########################################################################################################################

def main():
    conn = sqlite3.connect('message_queue.db')
    cursor = conn.cursor()

    try:
        while True:
            cursor.execute("SELECT id, topic, payload, status FROM message_queue WHERE status IN ('Inbound - Unsorted', 'Outbound - Unsent')")
            messages = cursor.fetchall()

            for message in messages:
                id, topic, payload, status = message
                if status == 'Inbound - Unsorted':
                    process_inbound_message(cursor, id, topic, payload)
                elif status == 'Outbound - Unsent':
                    process_outbound_message(cursor, id, topic, payload)

            conn.commit()
            time.sleep(0.25) # Sleep for 0.25 seconds to prevent excessive CPU usage
    finally:
        conn.close()

if __name__ == "__main__":
    main()
