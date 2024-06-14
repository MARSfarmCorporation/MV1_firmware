# This script is used to connect to the AWS IoT Core MQTT broker using websockets and the AWS IoT Core credentials.
# It also handles the incoming and outgoing messages from the broker.py service.
# Author: Drew Thomas - 08.14.2020

from time import sleep
from datetime import datetime
from awscrt import http, auth, io, mqtt
from awsiot import mqtt_connection_builder
from concurrent.futures import Future, TimeoutError
import sys
import os
import threading
import argparse
import traceback
import signal
import socket
import json
import subprocess
import datetime
import logging
import uuid
import time
from WebSocketUtil import secure_database_write, secure_database_update
from Sys_Conf import DEVICE_ID, SERIAL_NUMBER

# Setup logging to file
logging.basicConfig(filename='../logs/websocket_comms_log', level=logging.DEBUG)

# Global variables
is_sample_done = threading.Event()
trial_topic = "trial/" + DEVICE_ID
trial2_topic = "trial2/" + DEVICE_ID
cloud_device_control_topic = "cloud-device-control/" + DEVICE_ID
pong_topic = "pong/" + DEVICE_ID
ping_topic = "ping/" + DEVICE_ID
mqtt_connection = None

# Class to hold the locked data for threading
class LockedData:
    def __init__(self):
        self.lock = threading.Lock()
        self.disconnect_called = False
        self.reconnection_attempts = 0

locked_data = LockedData()

# Dictionary to hold heartbeat data
ping_tracker = {}

###########################################################################################################################
# CREDENTIALS
###########################################################################################################################

# Parse command line arguments for the AWS IoT Core endpoint, signing region, and client ID
parser = argparse.ArgumentParser(description="Send and receive messages through an MQTT connection.")
parser.add_argument("--endpoint", action="store", type=str, default="a28ud61a8gem1b-ats.iot.us-east-2.amazonaws.com", help="")
parser.add_argument("--signing_region", action="store", type=str, default="us-east-2", help="")
parser.add_argument("--client_id", action="store", type=str, default=SERIAL_NUMBER, help="")
args = parser.parse_args()

# AWS IoT Core credentials
device_cert = "/home/pi/certs/device.pem.crt.crt"
private_key = "/home/pi/certs/private.pem.key"
ca_cert = "/home/pi/certs/AmazonRootCA1.pem"
iot_endpoint = "https://cflwxka0nrnjy.credentials.iot.us-east-2.amazonaws.com/role-aliases/websocket-role-alias-5/credentials"
thing_name = args.client_id

# Function to get the temporary credentials from the AWS IoT Core using curl
def get_iot_temporary_credentials():
    curl_command = ["curl", "--cert", device_cert, "--key", private_key, "-H", "x-amzn-iot-thingname: " + thing_name, "--cacert", ca_cert, iot_endpoint]
    output = subprocess.check_output(curl_command, stderr=subprocess.DEVNULL).decode("utf-8")
    return json.loads(output)['credentials']

# Deprecated method of getting credentials due to the refresh thread
#credentials_data = get_iot_temporary_credentials()
#credentials_provider = auth.AwsCredentialsProvider.new_static(credentials_data['accessKeyId'], credentials_data['secretAccessKey'], credentials_data['sessionToken'])

def refresh_credentials():
    global credentials_provider
    MIN_REFRESH_INTERVAL = 60  # Minimum interval of 60 seconds between refreshes
    
    while not is_sample_done.is_set():
        try:
            # Get the new credentials
            credentials_data = get_iot_temporary_credentials()
            credentials_provider = auth.AwsCredentialsProvider.new_static(credentials_data['accessKeyId'], credentials_data['secretAccessKey'], credentials_data['sessionToken'])
            
            # Calculate the time until expiration
            expiration_time = datetime.datetime.strptime(credentials_data['expiration'], "%Y-%m-%dT%H:%M:%SZ")
            current_time = datetime.datetime.utcnow()
            time_until_expiration = (expiration_time - current_time).total_seconds()

            # Calculate the sleep time (1 minute before expiration)
            sleep_time = time_until_expiration - 60  # Subtract 1 minute in seconds

            # Ensure the sleep time is reasonable
            sleep_time = max(sleep_time, MIN_REFRESH_INTERVAL)

            # Sleep until it's time to refresh
            sleep(sleep_time)
        except Exception as e:
            logging.error(f"Error refreshing credentials: {e}")
            # Add a short sleep to prevent tight looping in case of error
            sleep(60)

###########################################################################################################################
# FUNCTIONS
###########################################################################################################################

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))

    with locked_data.lock:
        locked_data.reconnection_attempts += 1
        if locked_data.reconnection_attempts > 5:  # Change 5 to any threshold you prefer
            exit("Exceeded maximum reconnection attempts.")

# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    with locked_data.lock:
        locked_data.reconnection_attempts = 0  # Reset the counter upon successful reconnection

# callback when the servise needs to exit
def exit(msg_or_exception):
    if isinstance(msg_or_exception, Exception):
        print("Exiting sample due to exception.")
        traceback.print_exception(msg_or_exception.__class__, msg_or_exception, sys.exc_info()[2])
    else:
        print("Exiting sample:", msg_or_exception)

    with locked_data.lock:
        if not locked_data.disconnect_called:
            print("Disconnecting...")
            locked_data.disconnect_called = True
            future = mqtt_connection.disconnect()
            future.add_done_callback(on_disconnected)

# Callback when the connection is disconnected
def on_disconnected(disconnect_future):
    print("Disconnected.")
    is_sample_done.set()

# performs graceful shutdown when SIGINT or SIGTERM signal is received
def shutdown_server(signum, frame):
    print("Shutting down server...")
    
    # Signal the refresh thread to stop
    is_sample_done.set()

    # Disconnect from MQTT
    exit("Shutting down due to signal.")

    # Close the server socket
    server_socket.close()

    # Remove the Unix socket file
    socket_file = "/tmp/websocket_comms.sock"
    if os.path.exists(socket_file):
        os.remove(socket_file)

    # Exit the program
    sys.exit(0)

# Sends a ping to the IoT Core endpoint to keep the connection alive
def send_ping():
    ping_id = str(uuid.uuid4())  # Generate a unique ID for the ping
    ping_tracker[ping_id] = False  # Initialize to False indicating pong not yet received

    # Construct the ping message payload with the unique ID
    ping_payload = json.dumps({"ping": ping_id})
    mqtt_connection.publish(
        topic=ping_topic,
        payload=ping_payload,
        qos=mqtt.QoS.AT_LEAST_ONCE
    )
    return ping_id

# Callback to handle incoming pongs
def handle_pong(topic, payload, **kwargs):
    pong_message = json.loads(payload.decode('utf-8'))
    pong_id = pong_message.get("pong")

    if pong_id in ping_tracker:
        ping_tracker[pong_id] = True  # Mark that the pong has been received

def wait_for_pong(ping_id, timeout=300):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if ping_tracker.get(ping_id):
            print("Pong received for ping ID:", ping_id)
            return True
        sleep(1)  # Wait a bit before checking again

    # Timeout elapsed without receiving pong
    print("Pong not received for ping ID:", ping_id)
    return False

# Restarts the websocket_comms service if the connection is lost
def restart_service():
    print("Restarting the MQTT service...")
    subprocess.call(['sudo', 'systemctl', 'restart', 'websocket_comms.service'])

###########################################################################################################################
# MESSAGE HANDLERS
###########################################################################################################################

# Callback to handle incoming messages
def handle_inbound_message(topic, payload, **kwargs):
    print(f"Received message from topic '{topic}': {payload.decode('utf-8')}")

    # Publish a response to the log/response topic for this device
    mqtt_connection.publish(
        topic="log/response/" + DEVICE_ID,
        payload="Data received for device: " + SERIAL_NUMBER + ", on Topic: " + topic,
        qos=mqtt.QoS.AT_LEAST_ONCE
    )
    print("Response sent")

    # Convert the payload to a JSON string and set the default inbound status
    payload_json = payload.decode('utf-8')
    status = "Inbound - Unsorted"

    # Connect to the SQLite database
    try:
        secure_database_write(topic, payload_json, status)
    except Exception as e:
        print(f"Error logging device data: {e}")

# Function to publish a message coming from the broker.py service to the AWS IoT Endpoint
def handle_outbound_message(outbound_message):
    # Extract the database id, message topic, and message payload from the received message
    id = outbound_message.get("id")
    topic = outbound_message.get("topic")
    payload = outbound_message.get("payload")

    result_future = Future()

    with open('../logs/Broker_Log.txt', 'a') as file:
        file.write(f"websocket_comms.py: attempting to publish ID: {id}, Topic: {topic}, and Payload: {payload} \n")

    # Check if the topic and payload are valid
    if topic and payload:
        try:
            # Publish the message to the AWS IoT Endpoint as a future object
            publish_future, _ = mqtt_connection.publish(
                topic=topic,
                payload=json.dumps(payload),
                qos=mqtt.QoS.AT_LEAST_ONCE
            )
            #with open('../logs/Broker_Log.txt', 'a') as file:
            #    file.write(f"websocket_comms.py: MQTT Publish success.\n")
            #with open('../logs/Broker_Log.txt', 'a') as file:
            #    file.write(f"websocket_comms.py: MQTT publish Future: {publish_future}\n")
            
            try:
                # Wait for up to 5 seconds for the publish future to complete
                publish_future.result(timeout=5)
                
                # If it's here, it means the publish was successful
                result_future.set_result("success")
            #    with open('../logs/Broker_Log.txt', 'a') as file:
            #        file.write(f"websocket_comms.py: on_publish_complete future.result: {result_future} \n")
                print("Message published successfully.")
            except TimeoutError:
                print("Publish operation timed out.")
                with open('../logs/Broker_Log.txt', 'a') as file:
                    file.write("websocket_comms.py: Publish operation timed out.\n")
                result_future.set_result("failure")
            except Exception as e:
                print(f"Publish failed: {e}")
                with open('../logs/Broker_Log.txt', 'a') as file:
                    file.write(f"websocket_comms.py: Publish failed: {e}\n")
                result_future.set_result("failure")

            # Get the publish status from the result future
            publish_status = result_future.result()

            # Update the database status based on the publish status
            if publish_status == "success":
                status = "Outbound - Sent"
            #    with open('../logs/Broker_Log.txt', 'a') as file:
            #        file.write(f"websocket_comms.py: attempting to change status, ID: {id}, Status: {status} \n")
                secure_database_update(id, status)
            else:
                status = "Outbound - Pending Connection Restore"
                with open('../logs/Broker_Log.txt', 'a') as file:
                    file.write(f"websocket_comms.py: failed to change status, ID: {id}, Status: {status} \n")
                secure_database_update(id, status)

        except Exception as e:
            print(f"MQTT Publish failed: {e}")
            with open('../logs/Broker_Log.txt', 'a') as file:
                file.write(f"websocket_comms.py: MQTT Publish failed: {e}\n")
            return  # Exit the function if the publish operation fails
    else:
        print("Invalid message format. Expected 'topic' and 'payload' fields.")
        with open('../logs/Broker_Log.txt', 'a') as file:
            file.write(f"websocket_comms.py: Invalid message format passed to 'handle_outbound_message' function. Expected 'topic' and 'payload' fields.\n")

# Callback to handle incoming messages from the job_socket to the websocket_comms service
def handle_job_socket_jobID(jobID): #not finished
    # Subscribe to the "$aws/things/{thing_name}/jobs/{jobId}/update/accepted" topic with "thing_name" and "jobId" replaced with the appropriate values
    #mqtt_connection.subscribe(topic=f"$aws/things/{SERIAL_NUMBER}/jobs/{jobID}/update/accepted", qos=mqtt.QoS.AT_LEAST_ONCE, callback=handle_update_accepted)
    print("JobID received: " + jobID)
    with open('../logs/Job_Agent_Log.txt', 'a') as file:
        file.write(f"websocket_comms.py: jobID: {jobID}\n")

# Function to publish Job messages coming from the job_socket to the AWS IoT Endpoint
def handle_job_socket_publish(job_message):
    # Extract the topic and payload from the received message
    topic = job_message.get("topic")
    payload = job_message.get("payload")

    # Check if the topic and payload are valid
    if topic and payload:
        # Publish the message to the AWS IoT Endpoint
        mqtt_connection.publish(
            topic=topic,
            payload=payload,
            qos=mqtt.QoS.AT_LEAST_ONCE
        )
        print(f"Published message to topic '{topic}': {payload}")
    else:
        print("Invalid message format. Expected 'topic' and 'payload' fields.")
        with open('../logs/Job_Agent_Log.txt', 'a') as file:
            file.write(f"websocket_comms.py: Invalid message format passed to 'handle_outbound_message' function. Expected 'topic' and 'payload' fields.\n")

# Function used by heartbeat thread to send pings to the IoT Core endpoint
def connection_monitor():
    while not is_sample_done.is_set():
        try:
            # Send a ping message and wait for a pong
            ping_id = send_ping()
            pong_received = wait_for_pong(ping_id, timeout=300)  # Wait up to 300 seconds for a pong

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if not pong_received:
                # Pong not received, take remedial action
                with open('../logs/heartbeat_log.txt', 'a') as file:
                    file.write(f"{current_time} - Connection Lost\n")
                print("Pong not received, restarting service or taking other action.")
                restart_service()
                break  # Optionally break the loop if you want the thread to end after taking action
            
            # Sleep for 5 minutes before sending the next ping
            sleep(300)
        except Exception as e:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open('../logs/heartbeat_log.txt', 'a') as file:
                file.write(f"{current_time} - Error in connection monitor thread: {e}\n")
            print(f"Error in connection monitor thread: {e}")


###########################################################################################################################
# SOCKETS
###########################################################################################################################

# Create the server socket outside of the broker_socket function
server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Register the signal handler for SIGTERM and SIGINT
signal.signal(signal.SIGTERM, shutdown_server)
signal.signal(signal.SIGINT, shutdown_server)

# Sets up the broker_socket to receive messages from the broker.py service
def broker_socket():
    # Socket file path
    socket_file = "/tmp/websocket_comms.sock"

    # Remove the socket file if it already exists
    if os.path.exists(socket_file):
        os.remove(socket_file)

    # Bind the socket to the file
    server_socket.bind(socket_file)

    # Listen for incoming connections
    server_socket.listen(1)

    print("broker_socket server waiting for connections...")

    while True:
        try:
            # Accept a connection
            connection, _ = server_socket.accept()

            # Receive the message in chunks. It keeps adding chunks the the end of the previous chunk until the next one is empty, then it stops
            chunks = []
            while True:
                chunk = connection.recv(4096)  # Buffer size of 4096 bytes
                if chunk:
                    chunks.append(chunk)
                else:
                     break

            # Combine the chunks and decode the message
            outbound_message = b''.join(chunks).decode()

            with open('../logs/Broker_Log.txt', 'a') as file:
                file.write(f"websocket_comms.py: Received from Socket: {outbound_message}\n")

            # Passes file to the outbound message handler
            handle_outbound_message(json.loads(outbound_message))

            # Sleep briefly to yield control and prevent tight looping
            sleep(0.1)

        except Exception as e:
            print(f"An error occurred while handling a connection: {e}")
            # Optionally, you can log the traceback or other details here

        finally:
            # Ensure the connection is closed, even if an error occurred
            connection.close()

    # Close the socket
    server_socket.close()

# ------------------------------------- # job_socket # ------------------------------------- #
# This socket is hosted on this script, and is used to receive jop updates from the Job_Agent.py script

def job_socket():
    # Socket file path
    socket_file = "/tmp/job_socket.sock"

    # Remove the socket file if it already exists
    if os.path.exists(socket_file):
        os.remove(socket_file)

    # Bind the socket to the file
    job_server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)  # Define the server_socket here
    job_server_socket.bind(socket_file)

    # Listen for incoming connections
    job_server_socket.listen(1)

    print("job_socket server waiting for connections...")

    while True:
        try:
            # Accept a connection
            connection, _ = job_server_socket.accept()

            # Receive the message in chunks. It keeps adding chunks to the end of the previous chunk until the next one is empty, then it stops
            chunks = []
            while True:
                chunk = connection.recv(1024)  # Buffer size of 1024 bytes
                if chunk:
                    chunks.append(chunk)
                else:
                    break

            # Combine the chunks and decode the message
            received_data = b''.join(chunks).decode()
            messages = received_data.split('\n')
            
            with open('../logs/Job_Agent_Log.txt', 'a') as file:
                file.write(f"websocket_comms.py: messages: {messages}\n")
            
            for message in messages:
                if message:  # Ignore empty strings resulting from trailing newlines
                    message_data = json.loads(message)

                    with open('../logs/Job_Agent_Log.txt', 'a') as file:
                        file.write(f"websocket_comms.py: message_data: {message_data}\n")

                    # Check the type of the message and route to the appropriate handler
                    message_type = message_data.get("type")
                    if message_type == "jobID":
                        handle_job_socket_jobID(message_data['jobID'])
                    elif message_type == "publish":
                        with open('../logs/Job_Agent_Log.txt', 'a') as file:
                            file.write(f"websocket_comms.py: message_type: {message_data}\n")
                        handle_job_socket_publish(message_data)
                    else:
                        print(f"Unknown message type: {message_type}")
                        with open('../logs/Job_Agent_Log.txt', 'a') as file:
                            file.write(f"websocket_comms.py: Unknown message type: {message_type}\n")
            
            # Sleep briefly to yield control and prevent tight looping
            sleep(0.1)
        except Exception as e:
            print(f"An error occurred while handling a connection: {e}")
            # Optionally, you can log the traceback or other details here

        finally:
            # Ensure the connection is closed, even if an error occurred
            connection.close()


###########################################################################################################################
# MAIN SCRIPT CONNECTION
###########################################################################################################################

if __name__ == '__main__':
    proxy_options = None

    mqtt_connection = mqtt_connection_builder.websockets_with_default_aws_signing(
        endpoint=args.endpoint,
        region=args.signing_region,
        credentials_provider=credentials_provider,
        http_proxy_options=proxy_options,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=args.client_id,
        clean_session=False,
        keep_alive_secs=60)
    print(mqtt_connection)

    print(f"Connecting to {args.endpoint} with client ID '{args.client_id}'...")
    connect_future = mqtt_connection.connect()
    print(connect_future)

    connect_future.result()
    print("Connected!")

    ###########################################################################################################################
    # MAIN SCRIPT THREADS
    ###########################################################################################################################

    # Start the refresh thread
    refresh_thread = threading.Thread(target=refresh_credentials)
    refresh_thread.start()

    # Start the Unix socket server in a separate thread.
    broker_socket_thread = threading.Thread(target=broker_socket)
    broker_socket_thread.start()

    # Start the job_socket server in a separate thread.
    job_socket_thread = threading.Thread(target=job_socket)
    job_socket_thread.start()

    # Start the connection monitor thread
    monitor_thread = threading.Thread(target=connection_monitor)
    monitor_thread.start()

    ###########################################################################################################################
    # MAIN SCRIPT SUBSCRIPTIONS
    ###########################################################################################################################

    # Subscribe to the trial topic, sends incoming messages to the handle_inbound_message callback
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=trial_topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=handle_inbound_message
    )

    # Subscribe to the trial2 topic, which allows for the new trial functionality on the web application to be used
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=trial2_topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=handle_inbound_message
    )

    # Subscribe to Device Control related topics
    mqtt_connection.subscribe(topic=cloud_device_control_topic, qos=mqtt.QoS.AT_LEAST_ONCE, callback=handle_inbound_message)

    # Subscribing to Job-related topics
    mqtt_connection.subscribe(topic=f"$aws/things/{thing_name}/jobs/notify-next", qos=mqtt.QoS.AT_LEAST_ONCE, callback=handle_inbound_message)
    mqtt_connection.subscribe(topic=f"$aws/things/{thing_name}/jobs/$next/get/accepted", qos=mqtt.QoS.AT_LEAST_ONCE, callback=handle_inbound_message)
    mqtt_connection.subscribe(topic=f"$aws/things/{thing_name}/jobs/$next/get/rejected", qos=mqtt.QoS.AT_LEAST_ONCE, callback=handle_inbound_message)
    mqtt_connection.subscribe(topic=f"$aws/things/{thing_name}/jobs/$next/start/accepted", qos=mqtt.QoS.AT_LEAST_ONCE, callback=handle_inbound_message)
    mqtt_connection.subscribe(topic=f"$aws/things/{thing_name}/jobs/$next/start/rejected", qos=mqtt.QoS.AT_LEAST_ONCE, callback=handle_inbound_message)

    # Subscribing to the pong topic
    mqtt_connection.subscribe(
        topic=pong_topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=handle_pong
    )
    
    subscribe_result = subscribe_future.result()
    print(f"Subscribed with {str(subscribe_result['qos'])}")
