# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.

from time import sleep
from awscrt import http, auth, io, mqtt
from awsiot import mqtt_connection_builder
from concurrent.futures import Future
import sys
import os
import threading
import sqlite3
import argparse
import traceback
import signal
import socket
import json
import subprocess
import datetime
from uuid import uuid4
from Sys_Conf import DEVICE_ID, SERIAL_NUMBER

# Parse command line arguments for the AWS IoT Core endpoint, signing region, and client ID
parser = argparse.ArgumentParser(description="Send and receive messages through an MQTT connection.")
parser.add_argument("--endpoint", action="store", type=str, default="a28ud61a8gem1b-ats.iot.us-east-2.amazonaws.com", help="")
parser.add_argument("--signing_region", action="store", type=str, default="us-east-2", help="")
parser.add_argument("--client_id", action="store", type=str, default=SERIAL_NUMBER, help="")
args = parser.parse_args()

# Global variables
is_sample_done = threading.Event()
trial_topic = "trial/" + DEVICE_ID
mqtt_connection = None

# Class to hold the locked data for threading
class LockedData:
    def __init__(self):
        self.lock = threading.Lock()
        self.disconnect_called = False
        self.reconnection_attempts = 0

locked_data = LockedData()

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

# Create the credentials provider
credentials_data = get_iot_temporary_credentials()
credentials_provider = auth.AwsCredentialsProvider.new_static(credentials_data['accessKeyId'], credentials_data['secretAccessKey'], credentials_data['sessionToken'])

def refresh_credentials():
    global credentials_provider
    while not is_sample_done.is_set():
        # Get the new credentials
        credentials_data = get_iot_temporary_credentials()
        credentials_provider = auth.AwsCredentialsProvider.new_static(credentials_data['accessKeyId'], credentials_data['secretAccessKey'], credentials_data['sessionToken'])
        
        # Calculate the time until the next refresh (11 hours before expiration)
        expiration_time = datetime.datetime.strptime(credentials_data['expiration'], "%Y-%m-%dT%H:%M:%SZ")
        refresh_time = expiration_time - datetime.timedelta(hours=11)
        sleep_time = (refresh_time - datetime.datetime.utcnow()).total_seconds()

        # Sleep until it's time to refresh
        sleep(max(sleep_time, 0))

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

# Callback to handle incoming messages
def on_message_received(topic, payload, **kwargs):
    print(f"Received message from topic '{topic}': {payload.decode('utf-8')}")

    # Convert the payload to a JSON string
    payload_json = payload.decode('utf-8')
    status = "Inbound - Unsorted"

    # Connect to the SQLite database
    conn = sqlite3.connect('message_queue.db')
    cursor = conn.cursor()

    # Insert the message into the queue
    cursor.execute("INSERT INTO message_queue (topic, payload, status) VALUES (?, ?, ?)", (topic, payload_json, status))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

# Function to publish a message coming from the broker.py service to the AWS IoT Endpoint
def handle_outbound_message(outbound_message):
    # Extract the topic and payload from the received message
    topic = outbound_message.get("topic")
    payload = outbound_message.get("payload")

    # Check if the topic and payload are valid
    if topic and payload:
        # Publish the message to the AWS IoT Endpoint
        mqtt_connection.publish(
            topic=topic,
            payload=json.dumps(payload),
            qos=mqtt.QoS.AT_LEAST_ONCE
        )
        print(f"Published message to topic '{topic}': {payload}")
    else:
        print("Invalid message format. Expected 'topic' and 'payload' fields.")

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

# Create the server socket outside of the unix_socket_server function
server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Register the signal handler for SIGTERM and SIGINT
signal.signal(signal.SIGTERM, shutdown_server)
signal.signal(signal.SIGINT, shutdown_server)

# Sets up the Unix socket server to receive messages from the broker.py service
def unix_socket_server():
    # Socket file path
    socket_file = "/tmp/websocket_comms.sock"

    # Remove the socket file if it already exists
    if os.path.exists(socket_file):
        os.remove(socket_file)

    # Bind the socket to the file
    server_socket.bind(socket_file)

    # Listen for incoming connections
    server_socket.listen(1)

    print("Unix socket server waiting for connections...")

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

            # Handle the message
            handle_outbound_message(json.loads(outbound_message))

        except Exception as e:
            print(f"An error occurred while handling a connection: {e}")
            # Optionally, you can log the traceback or other details here

        finally:
            # Ensure the connection is closed, even if an error occurred
            connection.close()

    # Close the socket
    server_socket.close()

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
        keep_alive_secs=30)
    print(mqtt_connection)

    print(f"Connecting to {args.endpoint} with client ID '{args.client_id}'...")
    connect_future = mqtt_connection.connect()
    print(connect_future)

    connect_future.result()
    print("Connected!")

    # Start the refresh thread
    refresh_thread = threading.Thread(target=refresh_credentials)
    refresh_thread.start()

    # Start the Unix socket server in a separate thread.
    unix_socket_server_thread = threading.Thread(target=unix_socket_server)
    unix_socket_server_thread.start()

    # Subscribe to the topic
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic="testing/test",
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received
    )

    subscribe_result = subscribe_future.result()
    print(f"Subscribed with {str(subscribe_result['qos'])}")
