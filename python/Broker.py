import sqlite3
import time
import json
import socket
import subprocess
import os
import threading
from Sys_Conf import DEVICE_ID, SERIAL_NUMBER
from WebSocketUtil import log_job_fail, secure_database_update, aws_enqueue
from Lights import Light
from Pump_Control import test_pump

###########################################################################################################################
# DEFINE TOPICS
###########################################################################################################################

trial_topic = 'trial/' + DEVICE_ID
trial2_topic = 'trial2/' + DEVICE_ID
#device_control_topic = 'device-control/' + DEVICE_ID # Remove this topic as it is not used
cloud_device_control_topic = 'cloud-device-control/' + DEVICE_ID
job_notify_topic = f'$aws/things/{SERIAL_NUMBER}/jobs/notify-next'
secure_tunnel_topic = f'$aws/things/{SERIAL_NUMBER}/tunnels/notify'

###########################################################################################################################
# SEMAPHORES
###########################################################################################################################

pump_lock_file = '/home/pi/Desktop/MV1_firmware/python/pump_lock.lock'
pump_lock_timeout = 1500  # 1500 seconds = 25 minutes

###########################################################################################################################
# SPECIAL HANDLER FUNCTIONS
###########################################################################################################################

def spawn_job_agent(id, payload):
    try:
        # write the payload to Job_Agent_Log.txt, on a new line each time (make sure the file is there), with the prefix "Broker.py: "
        with open('../logs/Job_Agent_Log.txt', 'a') as file:
            file.write(f"Broker.py: {payload}\n")

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
                return_code = result.returncode
                log_job_fail(return_code)
                error_message = result.stderr.decode('utf-8')  # Decode stderr to string
                print(f"Job Error Unknown: {error_message}")  # Print the error message
                # Write the error message to Job_Agent_Log.txt
                with open('../logs/Job_Agent_Log.txt', 'a') as log_file:
                    log_file.write(f"Broker.py: Job Error Unknown with return code {return_code}: {error_message}\n")
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

def trial2_handler(payload, id):
    try:
        # Parse the incoming payload from string to dictionary
        payload_dict = json.loads(payload)
        
        # Extract the 'formatted_trial' object from the payload
        formatted_trial = payload_dict.get("formatted_trial", {})
        
        # Convert the 'formatted_trial' object back to a string, but formatted as required
        formatted_trial_str = f"trial={json.dumps(formatted_trial)}"
        
        # Write the formatted 'formatted_trial' string to trial.py
        with open('trial.py', 'w') as file:
            file.write(formatted_trial_str)
        
        # Update the status in the database as 'Inbound - Sorted'
        status = 'Inbound - Sorted'
        secure_database_update(id, status)

        create_response_topic = f'trialResponseCreate/{DEVICE_ID}'
        aws_enqueue(create_response_topic, payload_dict)
        
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

def cloud_device_control(payload, id):
    try: 
        # Assuming payload is a JSON string; parse it into a dictionary
        payload_dict = json.loads(payload)
        
        # Check which operation the user wants to perform, based on the "command" key.
        command = payload_dict.get("control")
        value = payload_dict.get("value")
        if command == "LED":
            # Check if "value" is 1, and flash the LED if it is. Otherwise, update the status to "Inbound - Unsortable - Unknown"
            if value == 1:
                light = Light()
                light.flash_all()
                status = 'Inbound - Sorted'
            else:
                print("Unknown LED value received from the Web Application")
                status = 'Inbound - Unsortable - Unknown'
        elif command == "PUMP":
            try:
                test_pump(value)
                status = 'Inbound - Sorted'
            except Exception as e:
                print(f"Error running pump: {e}")
                status = 'Inbound - Unsortable - Unknown'
        else:
            print("Command type not recognized from message ID: {id}")
            status = 'Inbound - Unsortable - Unknown'
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON payload when trying to run a user command from the Web Application: {e}")
        status = 'Inbound - Unsortable - Unknown'
        # Optionally blink the lights red to indicate a parse error
        light = Light()
        light.blink_red()
    except Exception as e:
        print(f"Error processing inbound message: {e}")
        status = 'Inbound - Unsortable - Unknown'
        # Blink the lights red to indicate a general error
        light = Light()
        light.blink_red()
    secure_database_update(id, status)

def secure_tunnel(payload, id):
    # Parse the payload
    try:
        with open('../logs/Job_Agent_Log.txt', 'a') as log_file:
            log_file.write(f"Broker.py: attempting to parse payload: {payload}\n")
        data = json.loads(payload)
        region = data['region']
        client_access_token = data['clientAccessToken']
        with open('../logs/Job_Agent_Log.txt', 'a') as log_file:
            log_file.write(f"Broker.py: attempting to start a secure tunnel with region: {region} and token {client_access_token}\n")
        print(f"Region: {region}, Client Access Token: {client_access_token}")
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error parsing payload: {e}")
        return

    # Construct the command
    command = f"../../localproxy -r {region} -d {client_access_token} -a localhost:22"
    with open('../logs/Job_Agent_Log.txt', 'a') as log_file:
        log_file.write(f"Broker.py: Attempting to open secure tunnel via the command: {command}\n")
    print(f"Command: {command}")

    # Start the subprocess
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with open('../logs/Job_Agent_Log.txt', 'a') as log_file:
            log_file.write(f"Broker.py: Subprocess started with PID: {process.pid}\n")
        print(f"Subprocess started with PID: {process.pid}")

        # Optionally, you can update the database status immediately, or handle it after the process completes.
        # This example updates the status immediately after starting the process.
        status = 'Inbound - Sorted'
        secure_database_update(id, status)
        print(f"Database entry with ID {id} updated to 'Inbound - Sorted'.")

    except Exception as e:
        print(f"Error starting subprocess: {e}")
        # Optionally, update the database with a failure status
        status = "Error - Inbound - Unsortable"
        secure_database_update(id, status)
        with open('../logs/Job_Agent_Log.txt', 'a') as log_file:
            log_file.write(f"Broker.py: Error starting secure tunnel: {e}\n")
        print(f"Database entry with ID {id} updated to 'Error starting secure tunnel'.")

###########################################################################################################################
# INBOUND MESSAGE HANDLING
###########################################################################################################################

# This function handles inbound messages and sorts them via their topic. It then updates the status in the database.
def process_inbound_message(cursor, id, topic, payload):
    try:
        # Defined topics are handled here via their respective functions
        if topic == trial_topic:
            trial_handler(payload, id)
        elif topic == trial2_topic:
            trial2_handler(payload, id)
        elif topic == job_notify_topic:
            spawn_job_agent(id, payload)
        #elif topic == device_control_topic:
        #    device_control(payload, id)
        elif topic == cloud_device_control_topic:
            cloud_device_control(payload, id)
        elif topic == secure_tunnel_topic:
            secure_tunnel(payload, id)
        else:
            # Handle other topics as needed
            pass
    except Exception as e:
        print(f"Error processing inbound message: {e}")
        with open('../logs/Broker_Log.txt', 'a') as file:
            file.write(f"Broker.py: Error sorting inbound message: {e}\n")
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

# This function handles outbound messages that were unable to send due to a rare connection error, generally only when the socket to websocket_comms is lost after a message is sent to it.
# A more elegant solution can likely be made with an independant script that runs nightly to check for lost messages, but this is a simple solution for now.
def handle_lost_pending_messages():
    conn = sqlite3.connect('message_queue.db')
    cursor = conn.cursor()

    try:
        while True:
            cursor.execute("SELECT id, topic, payload, status FROM message_queue WHERE status = 'Outbound - Pending' ORDER BY id ASC LIMIT 50")
            messages = cursor.fetchall()

            for message in messages:
                id, topic, payload, status = message
                process_outbound_message(cursor, id, topic, payload)

            conn.commit()
            time.sleep(6013)  # Sleep for 100 minutes and 13 seconds to prevent excessive CPU usage, and to prevent recursively sending messages on the main loop
    finally:
        conn.close()

if __name__ == "__main__":
    # Start a thread to handle pending messages
    pending_messages_thread = threading.Thread(target=handle_pending_messages)
    pending_messages_thread.start()

    # Start a thread to handle lost pending messages
    lost_pending_messages_thread = threading.Thread(target=handle_lost_pending_messages)
    lost_pending_messages_thread.start()
    
    # Start the main loop
    main()
