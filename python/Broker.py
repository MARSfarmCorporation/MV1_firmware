import sqlite3
import time
import json
import socket
import subprocess
from Sys_Conf import DEVICE_ID, SERIAL_NUMBER

###########################################################################################################################
# DEFINE TOPICS
###########################################################################################################################

trial_topic = 'trial/' + DEVICE_ID
job_notify_topic = f'$aws/things/{SERIAL_NUMBER}/jobs/notify-next'

###########################################################################################################################
# SPECIAL HANDLER FUNCTIONS
###########################################################################################################################

def spawn_job_agent(cursor, id, payload):
    try:
        # Start the Job_Agent.py process and pass the payload
        result = subprocess.run(['python3', 'Job_Agent.py', payload],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                timeout=60)

        # Check the return code to determine the status
        if result.returncode == 0:
            cursor.execute("UPDATE message_queue SET status = 'Inbound - Sorted' WHERE id = ?", (id,))
        elif result.returncode == 1:
            cursor.execute("UPDATE message_queue SET status = 'Inbound - Unsortable - Job Error 1' WHERE id = ?", (id,))
        elif result.returncode == 2:
            cursor.execute("UPDATE message_queue SET status = 'Inbound - Unsortable - Job Error 2' WHERE id = ?", (id,))
        else:
            cursor.execute("UPDATE message_queue SET status = 'Inbound - Unsortable - Job Error Unknown' WHERE id = ?", (id,))
    
    except subprocess.TimeoutExpired as e:
        print(f"Error executing the script: {e}")
        cursor.execute("UPDATE message_queue SET status = 'Inbound - Unsortable - Timeout' WHERE id = ?", (id,))

    except Exception as e:
        print(f"Error executing the script: {e}")
        cursor.execute("UPDATE message_queue SET status = 'Inbound - Unsortable - Unknown' WHERE id = ?", (id,))

def trial_handler(payload):
    # Write the payload to trial.py
    with open('trial.py', 'w') as file:
        file.write(payload)

###########################################################################################################################
# INBOUND MESSAGE HANDLING
###########################################################################################################################

# This function handles inbound messages and sorts them via their topic. It then updates the status in the database.
def process_inbound_message(cursor, id, topic, payload):
    try:
        # Defined topics are handled here via their respective functions
        if topic == trial_topic:
            trial_handler(payload)
            cursor.execute("UPDATE message_queue SET status = 'Inbound - Sorted' WHERE id = ?", (id,))
        if topic == job_notify_topic:
            spawn_job_agent(cursor, id, payload)
        else:
            # Handle other topics as needed
            pass
    except Exception as e:
        print(f"Error processing inbound message: {e}")
        cursor.execute("UPDATE message_queue SET status = 'Inbound - Unsortable - Unrecognized Topic' WHERE id = ?", (id,))

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
        cursor.execute("UPDATE message_queue SET status = 'Outbound - Sent' WHERE id = ?", (id,))
    except Exception as e:
        print(f"Error sending outbound message: {e}")
        cursor.execute("UPDATE message_queue SET status = 'Outbound - Unsendable' WHERE id = ?", (id,))

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
