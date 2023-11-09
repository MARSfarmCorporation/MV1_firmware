import sqlite3
import time
import json
import socket
import subprocess
import threading
from Sys_Conf import DEVICE_ID, SERIAL_NUMBER
from WebSocketUtil import log_job_fail, secure_database_update
from Lights import Light

###########################################################################################################################
# DEFINE TOPICS
###########################################################################################################################

trial_topic = 'trial/' + DEVICE_ID
job_notify_topic = f'$aws/things/{SERIAL_NUMBER}/jobs/notify-next'
#Test
###########################################################################################################################
# SPECIAL HANDLER FUNCTIONS
###########################################################################################################################

def spawn_job_agent(payload):
    try:
        # write the payload to Job_Agent_Log.txt, on a new line each time (make sure the file is there), with the prefix "Broker.py: "
        #with open('../logs/Job_Agent_Log.txt', 'a') as file:
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

        # Blink the lights white to indicate a successful trial write
        light = Light()
        light.trial_received_success()
        
    except Exception as e:
        print(f"Error processing inbound message: {e}")
        status = 'Inbound - Unsortable - Unknown'
        secure_database_update(id, status)

        # Blink the lights red to indicate an error
        light = Light()
        light.blink_blue()

###########################################################################################################################
# INBOUND MESSAGE HANDLING
###########################################################################################################################

# This function handles inbound messages and sorts them via their topic. It then updates the status in the database.
def process_inbound_message(cursor, id, topic, payload):
    try:
        # Defined topics are handled here via their respective functions
        if topic == trial_topic:
            trial_handler(payload, id)
        elif topic == job_notify_topic:
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
        message = json.dumps({"id": id, "topic": topic, "payload": payload})
        
        # Send the message
        client_socket.sendall(message.encode())
        
        # Close the socket
        client_socket.close()
        
        # Update the status in the database
        status = 'Outbound - Pending'
        secure_database_update(id, status)
        #cursor.execute("UPDATE message_queue SET status = 'Outbound - Sent' WHERE id = ?", (id,))
    except Exception as e:
        print(f"Error sending outbound message: {e}")
        with open('../logs/Broker_Log.txt', 'a') as file:
            file.write(f"Broker.py: Error sending outbound message: {e}\n")
        status = 'Outbound - Pending Connection Restore'
        secure_database_update(id, status)
        #cursor.execute("UPDATE message_queue SET status = 'Outbound - Unsendable' WHERE id = ?", (id,))

###########################################################################################################################
# MESSAGE_QUEUE.DB POLLING
###########################################################################################################################

# Main loop to handle inbound and outbound messages
def main():
    try:
        # Try to connect to the database
        conn = sqlite3.connect('message_queue.db')
        cursor = conn.cursor()
    except sqlite3.Error as e:
        print(f"Database connection failed: {e}")
        # You can also log this error to a file
        with open('../logs/Broker_Log.txt', 'a') as file:
            file.write(f"Broker.py: Database connection failed: {e}\n")
        return  # Exit the function

    try:
        while True:
            try:
                # Try to execute the SQL query
                cursor.execute("SELECT id, topic, payload, status FROM message_queue WHERE status IN ('Inbound - Unsorted', 'Outbound - Unsent') ORDER BY id ASC LIMIT 10")
                messages = cursor.fetchall()
            except sqlite3.Error as e:
                print(f"SQL query execution failed: {e}")
                # Log this error to a file as well
                with open('../logs/Broker_Log.txt', 'a') as file:
                    file.write(f"Broker.py: SQL query execution failed: {e}\n")
                continue  # Skip this iteration and try again

            # write the payload to Job_Agent_Log.txt, on a new line each time (make sure the file is there), with the prefix "Job_Agent.py: "
            #with open('../logs/Broker_Log.txt', 'a') as file:
            #    file.write(f"Broker.py: attempting to send {messages}\n")
            
            for message in messages:
                id, topic, payload, status = message
                if status == 'Inbound - Unsorted':
                    process_inbound_message(cursor, id, topic, payload)
                elif status == 'Outbound - Unsent':
                    process_outbound_message(cursor, id, topic, payload)

            conn.commit()
            time.sleep(1) # Sleep for 1 second to prevent excessive CPU usage
    finally:
        conn.close()

# This function handles outbound messages that were unable to send due to a connection error.
def handle_pending_messages():
    conn = sqlite3.connect('message_queue.db')
    cursor = conn.cursor()

    try:
        while True:
            cursor.execute("SELECT id, topic, payload, status FROM message_queue WHERE status = 'Outbound - Pending Connection Restore' ORDER BY id ASC LIMIT 50")
            messages = cursor.fetchall()

            for message in messages:
                id, topic, payload, status = message
                process_outbound_message(cursor, id, topic, payload)

            conn.commit()
            time.sleep(60)  # Sleep for 1 minute to prevent excessive CPU usage
    finally:
        conn.close()

if __name__ == "__main__":
    # Start a thread to handle pending messages
    pending_messages_thread = threading.Thread(target=handle_pending_messages)
    pending_messages_thread.start()
    
    # Start the main loop
    main()
