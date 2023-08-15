# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.

from time import sleep
from awscrt import http, auth, io, mqtt
from awsiot import mqtt_connection_builder
from concurrent.futures import Future
import sys
import threading
import argparse
import traceback
import requests
from uuid import uuid4
from Sys_Conf import DEVICE_ID, SERIAL_NUMBER

parser = argparse.ArgumentParser(description="Send and receive messages through an MQTT connection.")
parser.add_argument("--endpoint", action="store", type=str, default="a28ud61a8gem1b-ats.iot.us-east-2.amazonaws.com", help="")
parser.add_argument("--signing_region", action="store", type=str, default="us-east-2", help="")
parser.add_argument("--client_id", action="store", type=str, default=SERIAL_NUMBER, help="")
args = parser.parse_args()

is_sample_done = threading.Event()

trial_topic = "trial/" + DEVICE_ID
tunnel_topic = f"$aws/things/mf-strawberry-test/tunnels/notify"
mqtt_connection = None
jobs_client = None
jobs_thing_name = args.client_id

class LockedData:
    def __init__(self):
        self.lock = threading.Lock()
        self.disconnect_called = False
        self.reconnection_attempts = 0

locked_data = LockedData()

device_cert = "/home/pi/certs/device.pem.crt.crt"
private_key = "/home/pi/certs/private.pem.key"
ca_cert = "/home/pi/certs/AmazonRootCA1.pem"
iot_endpoint = "https://cflwxka0nrnjy.credentials.iot.us-east-2.amazonaws.com/role-aliases/websocket-role-alias-5/credentials"
thing_name = args.client_id

def get_iot_temporary_credentials(device_cert, private_key, ca_cert, iot_endpoint, thing_name):
    headers = {
        "x-amzn-iot-thingname": thing_name
    }

    response = requests.get(
        iot_endpoint,
        cert=(device_cert, private_key),
        headers=headers,
        verify=ca_cert
    )

    if response.status_code == 200:
        return response.json()['credentials']
    else:
        response.raise_for_status()

def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))

    with locked_data.lock:
        locked_data.reconnection_attempts += 1
        if locked_data.reconnection_attempts > 5:  # Change 5 to any threshold you prefer
            exit("Exceeded maximum reconnection attempts.")

def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    with locked_data.lock:
        locked_data.reconnection_attempts = 0  # Reset the counter upon successful reconnection

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

def on_disconnected(disconnect_future):
    print("Disconnected.")
    is_sample_done.set()

# Callback to handle incoming messages
def on_message_received(topic, payload, **kwargs):
    print(f"Received message from topic '{topic}': {payload.decode('utf-8')}")

# Function to publish a message
def publish_message():
    mqtt_connection.publish(
        topic="testing/test",
        payload="Hello boiiiii",
        qos=mqtt.QoS.AT_LEAST_ONCE
    )

if __name__ == '__main__':
    proxy_options = None
   
    credentials = get_iot_temporary_credentials(device_cert, private_key, ca_cert, iot_endpoint, thing_name)
    
    credentials_provider = auth.AwsCredentialsProvider.new_static(credentials['accessKeyId'], credentials['secretAccessKey'], credentials['sessionToken'])
    print(credentials_provider)
    
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

    # Subscribe to the topic
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic="testing/test",
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received
    )

    subscribe_result = subscribe_future.result()
    print(f"Subscribed with {str(subscribe_result['qos'])}")

    # Main loop to publish a message every 2 seconds
    try:
        while True:
            publish_message()
            sleep(2)
    except KeyboardInterrupt:
        # Stop the loop when Ctrl+C is pressed
        pass
