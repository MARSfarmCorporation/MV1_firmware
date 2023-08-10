# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.

from time import sleep
from awscrt import http, auth, io, mqtt
from awsiot import iotshadow, mqtt_connection_builder, iotjobs
from concurrent.futures import Future
import sys
import threading
import argparse
import subprocess
import requests
import os
import fcntl
import json
import traceback
from uuid import uuid4
from Sys_Conf import DEVICE_ID, SERIAL_NUMBER

# argParse stuff
parser = argparse.ArgumentParser(description="Send and receive messages through and MQTT connection.")
parser.add_argument("--endpoint", action="store", type=str, default="a28ud61a8gem1b-ats.iot.us-east-2.amazonaws.com", help="")
parser.add_argument("--signing_region", action="store", type=str, default="us-east-2", help="")
parser.add_argument("--client_id", action="store", type=str, default="mf-strawberry-test", help="")
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
        self.shadow_value = None
        self.request_tokens = set()
        self.is_working_on_job = False
        self.is_next_job_waiting = False
        self.got_job_response = False


locked_data = LockedData()

lock_interface = threading.Lock()

# Adjust the paths for the certificate and key files as needed
device_cert = "/home/pi/certs/device.pem.crt.crt"
private_key = "/home/pi/certs/private.pem.key"
ca_cert = "/home/pi/certs/AmazonRootCA1.pem"
iot_endpoint = "https://cflwxka0nrnjy.credentials.iot.us-east-2.amazonaws.com/role-aliases/websocket-role-alias-5/credentials"
thing_name = args.client_id
curl_command = ["curl", "--cert", device_cert, "--key", private_key, "-H", "x-amzn-iot-thingname: " + thing_name, "--cacert", ca_cert, iot_endpoint]

try:
    # Run the curl command using subprocess
    output = subprocess.check_output(curl_command, stderr=subprocess.DEVNULL).decode("utf-8")
    credentials = json.loads(output)['credentials']
except subprocess.CalledProcessError as e:
    # In case of an error, print the error message
    print("Error executing the curl command:")
    print(e.output.decode("utf-8"))

shadow_thing_name = thing_name
shadow_property = "color"
SHADOW_VALUE_DEFAULT = "off"

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))

# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

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


# Disconnects and ends the program
def on_disconnected(disconnect_future):
    print("Disconnected.")
    is_sample_done.set()

def try_start_next_job():
    print("Trying to start the next job...")
    with locked_data.lock:
        if locked_data.is_working_on_job:
            print("Nevermind, already working on a job.")
            return

        if locked_data.disconnect_called:
            print("Nevermind, sample is disconnecting.")
            return

        locked_data.is_working_on_job = True
        locked_data.is_next_job_waiting = False

    print("Publishing request to start next job...")
    request = iotjobs.StartNextPendingJobExecutionRequest(thing_name=jobs_thing_name)
    publish_future = jobs_client.publish_start_next_pending_job_execution(request, mqtt.QoS.AT_LEAST_ONCE)
    publish_future.add_done_callback(on_publish_start_next_pending_job_execution)


def done_working_on_job():
    with locked_data.lock:
        locked_data.is_working_on_job = False
        try_again = locked_data.is_next_job_waiting

    if try_again:
        try_start_next_job()
        
# A list to hold all the pending jobs
available_jobs = []


def on_get_pending_job_executions_accepted(response):
    # type: (iotjobs.GetPendingJobExecutionsResponse) -> None
    with locked_data.lock:
        if (len(response.queued_jobs) > 0 or len(response.in_progress_jobs) > 0):
            print("Pending Jobs:")
            for job in response.in_progress_jobs:
                available_jobs.append(job)
                print(f"  In Progress: {job.job_id} @ {job.last_updated_at}")
            for job in response.queued_jobs:
                available_jobs.append(job)
                print(f"  {job.job_id} @ {job.last_updated_at}")
        else:
            print("No pending or queued jobs found!")
        locked_data.got_job_response = True


def on_get_pending_job_executions_rejected(error):
    # type: (iotjobs.RejectedError) -> None
    print(f"Request rejected: {error.code}: {error.message}")
    exit("Get pending jobs request rejected!")


def on_next_job_execution_changed(event):
    # type: (iotjobs.NextJobExecutionChangedEvent) -> None
    try:
        execution = event.execution
        if execution:
            print("Received Next Job Execution Changed event. job_id:{} job_document:{}".format(
                execution.job_id, execution.job_document))

            # Start job now, or remember to start it when current job is done
            start_job_now = False
            with locked_data.lock:
                if locked_data.is_working_on_job:
                    locked_data.is_next_job_waiting = True
                else:
                    start_job_now = True

            if start_job_now:
                try_start_next_job()

        else:
            print("Received Next Job Execution Changed event: None. Waiting for further jobs...")

    except Exception as e:
        exit(e)


def on_publish_start_next_pending_job_execution(future):
    # type: (Future) -> None
    try:
        future.result()  # raises exception if publish failed

        print("Published request to start the next job.")

    except Exception as e:
        exit(e)


def on_start_next_pending_job_execution_accepted(response):
    # type: (iotjobs.StartNextJobExecutionResponse) -> None
    try:
        if response.execution:
            execution = response.execution
            print("Request to start next job was accepted. job_id:{} job_document:{}".format(
                execution.job_id, execution.job_document))

            # To emulate working on a job, spawn a thread that sleeps for a few seconds
            job_thread = threading.Thread(
                target=lambda: job_thread_fn(execution.job_id, execution.job_document),
                name='job_thread')
            job_thread.start()
        else:
            print("Request to start next job was accepted, but there are no jobs to be done. Waiting for further jobs...")
            done_working_on_job()

    except Exception as e:
        exit(e)


def on_start_next_pending_job_execution_rejected(rejected):
    # type: (iotjobs.RejectedError) -> None
    exit("Request to start next pending job rejected with code:'{}' message:'{}'".format(
        rejected.code, rejected.message))


def job_thread_fn(job_id, job_document):
    try:
        print("Starting local work on job...")
        for step in job_document["steps"]:
            print(step)
            if(step["action"]["name"] == "Reboot"):
                #subprocess.run(['bash', step["action"]["input"]["path"]+step["action"]["input"]["handler"]], check=True)
                print("I don't want to actually do a reboot until it gets implemented properly")
            if(step["action"]["name"] == "OTA_Update"):
                subprocess.run(['bash', step["action"]["input"]["path"]+"ota_update.sh"], check=True)
            if(step["action"]["name"] == "download-file.sh"):
                response = requests.get(step["action"]["input"]["args"][0])
                with open(step["action"]["input"]["args"][1]+job_id,"w") as f:
                    f.write(str(response.content))
                    print(response.content)
        sleep(5)
        print("Done working on job.")

        print("Publishing request to update job status to SUCCEEDED...")
        request = iotjobs.UpdateJobExecutionRequest(
            thing_name=jobs_thing_name,
            job_id=job_id,
            status=iotjobs.JobStatus.SUCCEEDED)
        publish_future = jobs_client.publish_update_job_execution(request, mqtt.QoS.AT_LEAST_ONCE)
        publish_future.add_done_callback(on_publish_update_job_execution)

    except Exception as e:
        exit(e)


def on_publish_update_job_execution(future):
    # type: (Future) -> None
    try:
        future.result()  # raises exception if publish failed
        print("Published request to update job.")

    except Exception as e:
        exit(e)


def on_update_job_execution_accepted(response):
    # type: (iotjobs.UpdateJobExecutionResponse) -> None
    try:
        print("Request to update job was accepted.")
        done_working_on_job()
    except Exception as e:
        exit(e)


def on_update_job_execution_rejected(rejected):
    # type: (iotjobs.RejectedError) -> None
    exit("Request to update job status was rejected. code:'{}' message:'{}'.".format(
        rejected.code, rejected.message))

def on_get_shadow_accepted(response):
    # type: (iotshadow.GetShadowResponse) -> None
    try:
        with locked_data.lock:
            # check that this is a response to a request from this session
            try:
                locked_data.request_tokens.remove(response.client_token)
            except KeyError:
                print("Ignoring get_shadow_accepted message due to unexpected token.")
                return

            print("Finished getting initial shadow state.")
            if locked_data.shadow_value is not None:
                print("  Ignoring initial query because a delta event has already been received.")
                return

        if response.state:
            if response.state.delta:
                value = response.state.delta.get(shadow_property)
                if value:
                    print("  Shadow contains delta value '{}'.".format(value))
                    change_shadow_value(value)
                    return

            if response.state.reported:
                value = response.state.reported.get(shadow_property)
                if value:
                    print("  Shadow contains reported value '{}'.".format(value))
                    set_local_value_due_to_initial_query(response.state.reported[shadow_property])
                    return

        print("  Shadow document lacks '{}' property. Setting defaults...".format(shadow_property))
        change_shadow_value(SHADOW_VALUE_DEFAULT)
        return

    except Exception as e:
        exit(e)


def on_get_shadow_rejected(error):
    # type: (iotshadow.ErrorResponse) -> None
    try:
        # check that this is a response to a request from this session
        with locked_data.lock:
            try:
                locked_data.request_tokens.remove(error.client_token)
            except KeyError:
                print("Ignoring get_shadow_rejected message due to unexpected token.")
                return

        if error.code == 404:
            print("Thing has no shadow document. Creating with defaults...")
            change_shadow_value(SHADOW_VALUE_DEFAULT)
        else:
            exit("Get request was rejected. code:{} message:'{}'".format(
                error.code, error.message))

    except Exception as e:
        exit(e)


def on_shadow_delta_updated(delta):
    # type: (iotshadow.ShadowDeltaUpdatedEvent) -> None
    try:
        print("Received shadow delta event.")
        if delta.state and (shadow_property in delta.state):
            value = delta.state[shadow_property]
            if value is None:
                print("  Delta reports that '{}' was deleted. Resetting defaults...".format(shadow_property))
                change_shadow_value(SHADOW_VALUE_DEFAULT)
                return
            else:
                print("  Delta reports that desired value is '{}'. Changing local value...".format(value))
                if (delta.client_token is not None):
                    print("  ClientToken is: " + delta.client_token)
                change_shadow_value(value)
        else:
            print("  Delta did not report a change in '{}'".format(shadow_property))

    except Exception as e:
        exit(e)


def on_publish_update_shadow(future):
    # type: (Future) -> None
    try:
        future.result()
        print("Update request published.")
    except Exception as e:
        print("Failed to publish update request.")
        exit(e)


def on_update_shadow_accepted(response):
    # type: (iotshadow.UpdateShadowResponse) -> None
    try:
        # check that this is a response to a request from this session
        with locked_data.lock:
            try:
                locked_data.request_tokens.remove(response.client_token)
            except KeyError:
                print("Ignoring update_shadow_accepted message due to unexpected token.")
                return

        try:
            if response.state.reported is not None:
                if shadow_property in response.state.reported:
                    print("Finished updating reported shadow value to '{}'.".format(
                        response.state.reported[shadow_property]))  # type: ignore
                else:
                    print("Could not find shadow property with name: '{}'.".format(shadow_property))  # type: ignore
            else:
                print("Shadow states cleared.")  # when the shadow states are cleared, reported and desired are set to None
            print("Enter desired value: ")  # remind user they can input new values
        except BaseException:
            exit("Updated shadow is missing the target property")

    except Exception as e:
        exit(e)


def on_update_shadow_rejected(error):
    # type: (iotshadow.ErrorResponse) -> None
    try:
        # check that this is a response to a request from this session
        with locked_data.lock:
            try:
                locked_data.request_tokens.remove(error.client_token)
            except KeyError:
                print("Ignoring update_shadow_rejected message due to unexpected token.")
                return

        exit("Update request was rejected. code:{} message:'{}'".format(
            error.code, error.message))

    except Exception as e:
        exit(e)


def set_local_value_due_to_initial_query(reported_value):
    with locked_data.lock:
        locked_data.shadow_value = reported_value
    print("Enter desired value: ")  # remind user they can input new values


def change_shadow_value(value):
    with locked_data.lock:
        if locked_data.shadow_value == value:
            print("Local value is already '{}'.".format(value))
            print("Enter desired value: ")  # remind user they can input new values
            return

        print("Changed local shadow value to '{}'.".format(value))
        locked_data.shadow_value = value

        print("Updating reported shadow value to '{}'...".format(value))
        
        # use a unique token so we can correlate this "request" message to
        # any "response" messages received on the /accepted and /rejected topics
        token = str(uuid4())

        # if the value is "clear shadow" then send a UpdateShadowRequest with None
        # for both reported and desired to clear the shadow document completely.
        if value == "clear_shadow":
            tmp_state = iotshadow.ShadowState(
                reported=None,
                desired=None,
                reported_is_nullable=True,
                desired_is_nullable=True)
            request = iotshadow.UpdateShadowRequest(
                thing_name=shadow_thing_name,
                state=tmp_state,
                client_token=token,
            )
        # Otherwise, send a normal update request
        else:
            # if the value is "none" then set it to a Python none object to
            # clear the individual shadow property
            if value == "none":
                value = None

            request = iotshadow.UpdateShadowRequest(
                thing_name=shadow_thing_name,
                state=iotshadow.ShadowState(
                    reported={shadow_property: value},
                    desired={shadow_property: value},
                ),
                client_token=token,
            )

        future = shadow_client.publish_update_shadow(request, mqtt.QoS.AT_LEAST_ONCE)

        locked_data.request_tokens.add(token)

        future.add_done_callback(on_publish_update_shadow)


def user_input_thread_fn():
    # If we are not in CI, then take terminal input
    if not False:   #SHOULD BE if not cmdData.input_is_ci:
        while True:
            try:
                # Read user input
                new_value = input()

                # If user wants to quit sample, then quit.
                # Otherwise change the shadow value.
                if new_value in ['exit', 'quit']:
                    exit("User has quit")
                    break
                else:
                    change_shadow_value(new_value)

            except Exception as e:
                print("Exception on input thread.")
                exit(e)
                break
    # Otherwise, send shadow updates automatically
    else:
        try:
            messages_sent = 0
            while messages_sent < 5:
                cli_input = "Shadow_Value_" + str(messages_sent)
                change_shadow_value(cli_input)
                sleep(1)
                messages_sent += 1
            exit("CI has quit")
        except Exception as e:
            print("Exception on input thread (CI)")
            exit(e)

def on_trial_received(topic, payload):
    print(payload)
    with open("/home/pi/Desktop/trial.py", "w") as f:
        f.write(payload.decode("utf-8"))
        f.close()
    print("Implemented new trial")

def on_tunnel_notify(topic, payload):
    print(payload)
    tunnel_token = payload.decode("utf-8").split(",")[0].split(":")[1]
    os.system(f'/home/pi/Desktop/MV1_firmware/scripts/localproxy -t {tunnel_token} -d 22 -v 1 -r us-east-2')
    print("Launched tunnel")

if __name__ == '__main__':
    # Create the proxy options if the data is present in cmdData
    proxy_options = None
    #if cmdData.input_proxy_host is not None and cmdData.input_proxy_port != 0:
    #    proxy_options = http.HttpProxyOptions(
    #        host_name=cmdData.input_proxy_host,
    #        port=cmdData.input_proxy_port)

    # Create a default credentials provider and a MQTT connection from the command line data
    credentials_provider = auth.AwsCredentialsProvider.new_static(credentials['accessKeyId'],credentials['secretAccessKey'],credentials['sessionToken'])
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

    #if not cmdData.input_is_ci:
    print(f"Connecting to {iot_endpoint} with client ID '{args.client_id}'...")
    #else:
    #    print("Connecting to endpoint with client ID...")

    connect_future = mqtt_connection.connect()
    print(connect_future)
    jobs_client = iotjobs.IotJobsClient(mqtt_connection)
    shadow_client = iotshadow.IotShadowClient(mqtt_connection)
    print(jobs_client)
    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")
    
    try:
        # List the jobs queued and pending
        get_jobs_request = iotjobs.GetPendingJobExecutionsRequest(thing_name=jobs_thing_name)
        jobs_request_future_accepted, _ = jobs_client.subscribe_to_get_pending_job_executions_accepted(
            request=get_jobs_request,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=on_get_pending_job_executions_accepted
        )
        # Wait for the subscription to succeed
        jobs_request_future_accepted.result()

        jobs_request_future_rejected, _ = jobs_client.subscribe_to_get_pending_job_executions_rejected(
            request=get_jobs_request,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=on_get_pending_job_executions_rejected
        )
        # Wait for the subscription to succeed
        jobs_request_future_rejected.result()

        # Get a list of all the jobs
        get_jobs_request_future = jobs_client.publish_get_pending_job_executions(
            request=get_jobs_request,
            qos=mqtt.QoS.AT_LEAST_ONCE
        )
        # Wait for the publish to succeed
        get_jobs_request_future.result()
    except Exception as e:
        exit(e)
    
    
    try:
        # Subscribe to necessary topics.
        # Note that is **is** important to wait for "accepted/rejected" subscriptions
        # to succeed before publishing the corresponding "request".
        print("Subscribing to Next Changed events...")
        changed_subscription_request = iotjobs.NextJobExecutionChangedSubscriptionRequest(
            thing_name=jobs_thing_name)

        subscribed_future, _ = jobs_client.subscribe_to_next_job_execution_changed_events(
            request=changed_subscription_request,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=on_next_job_execution_changed)

        # Wait for subscription to succeed
        subscribed_future.result()

        print("Subscribing to Start responses...")
        start_subscription_request = iotjobs.StartNextPendingJobExecutionSubscriptionRequest(
            thing_name=jobs_thing_name)
        subscribed_accepted_future, _ = jobs_client.subscribe_to_start_next_pending_job_execution_accepted(
            request=start_subscription_request,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=on_start_next_pending_job_execution_accepted)

        subscribed_rejected_future, _ = jobs_client.subscribe_to_start_next_pending_job_execution_rejected(
            request=start_subscription_request,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=on_start_next_pending_job_execution_rejected)

        # Wait for subscriptions to succeed
        subscribed_accepted_future.result()
        subscribed_rejected_future.result()

        print("Subscribing to Update responses...")
        # Note that we subscribe to "+", the MQTT wildcard, to receive
        # responses about any job-ID.
        update_subscription_request = iotjobs.UpdateJobExecutionSubscriptionRequest(
            thing_name=jobs_thing_name,
            job_id='+')

        subscribed_accepted_future, _ = jobs_client.subscribe_to_update_job_execution_accepted(
            request=update_subscription_request,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=on_update_job_execution_accepted)

        subscribed_rejected_future, _ = jobs_client.subscribe_to_update_job_execution_rejected(
            request=update_subscription_request,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=on_update_job_execution_rejected)

        # Wait for subscriptions to succeed
        subscribed_accepted_future.result()
        subscribed_rejected_future.result()

        # Make initial attempt to start next job. The service should reply with
        # an "accepted" response, even if no jobs are pending. The response
        # will contain data about the next job, if there is one.
        # (Will do nothing if we are in CI)
        try_start_next_job()

    except Exception as e:
        exit(e)
        
    try:
        # Subscribe to necessary topics.
        # Note that is **is** important to wait for "accepted/rejected" subscriptions
        # to succeed before publishing the corresponding "request".
        print("Subscribing to Update responses...")
        #update_accepted_subscribed_future, _ = shadow_client.subscribe_to_update_shadow_accepted(
        #    request=iotshadow.UpdateShadowSubscriptionRequest(thing_name=thing_name),
        #    qos=mqtt.QoS.AT_LEAST_ONCE,
        #    callback=on_update_shadow_accepted)

        #update_rejected_subscribed_future, _ = shadow_client.subscribe_to_update_shadow_rejected(
        #    request=iotshadow.UpdateShadowSubscriptionRequest(thing_name=thing_name),
        #    qos=mqtt.QoS.AT_LEAST_ONCE,
        #    callback=on_update_shadow_rejected)

        # Wait for subscriptions to succeed
        #update_accepted_subscribed_future.result()
        #update_rejected_subscribed_future.result()

        #print("Subscribing to Get responses...")
        #get_accepted_subscribed_future, _ = shadow_client.subscribe_to_get_shadow_accepted(
        #    request=iotshadow.GetShadowSubscriptionRequest(thing_name=thing_name),
        #    qos=mqtt.QoS.AT_LEAST_ONCE,
        #    callback=on_get_shadow_accepted)

        #get_rejected_subscribed_future, _ = shadow_client.subscribe_to_get_shadow_rejected(
        #    request=iotshadow.GetShadowSubscriptionRequest(thing_name=thing_name),
        #    qos=mqtt.QoS.AT_LEAST_ONCE,
        #    callback=on_get_shadow_rejected)

        # Wait for subscriptions to succeed
        #get_accepted_subscribed_future.result()
        #get_rejected_subscribed_future.result()

        #print("Subscribing to Delta events...")
        #delta_subscribed_future, _ = shadow_client.subscribe_to_shadow_delta_updated_events(
        #    request=iotshadow.ShadowDeltaUpdatedSubscriptionRequest(thing_name=thing_name),
        #    qos=mqtt.QoS.AT_LEAST_ONCE,
        #    callback=on_shadow_delta_updated)

        # Wait for subscription to succeed
        #delta_subscribed_future.result()

        # The rest of the sample runs asynchronously.

        # Issue request for shadow's current state.
        # The response will be received by the on_get_accepted() callback
        #print("Requesting current shadow state...")

        #with locked_data.lock:
            # use a unique token so we can correlate this "request" message to
            # any "response" messages received on the /accepted and /rejected topics
        #    token = str(uuid4())

        #    publish_get_future = shadow_client.publish_get_shadow(
        #        request=iotshadow.GetShadowRequest(thing_name=shadow_thing_name, client_token=token),
        #        qos=mqtt.QoS.AT_LEAST_ONCE)

        #    locked_data.request_tokens.add(token)

        # Ensure that publish succeeds
        #publish_get_future.result()

        # Launch thread to handle user input.
        # A "daemon" thread won't prevent the program from shutting down.
        #print("Launching thread to read user input...")
        #user_input_thread = threading.Thread(target=user_input_thread_fn, name='user_input_thread')
        #user_input_thread.daemon = True
        #user_input_thread.start()
    except Exception as e:
        exit(e)
    try:
        print("Subscribing to topic '{}'...".format(trial_topic))
        subscribe_future, packet_id = mqtt_connection.subscribe(
            topic=trial_topic, 
            qos=mqtt.QoS.AT_LEAST_ONCE, 
            callback=on_trial_received)
    except Exception as e:
        exit(e)
    try:
        print("Subscribing to topic '{}'...".format(tunnel_topic))
        subscribe_future, packet_id = mqtt_connection.subscribe(
            topic=tunnel_topic, 
            qos=mqtt.QoS.AT_LEAST_ONCE, 
            callback=on_tunnel_notify)
    except Exception as e:
        exit(e)
    while not is_sample_done.is_set():
        sleep(10)
        with open("/home/pi/Desktop/MV1_firmware/logs/queue.txt", "r") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            contents = f.read()
        with open("/home/pi/Desktop/MV1_firmware/logs/cache.txt", "a+") as f:
            f.write(contents+"\n")
            f.seek(0)
            contents = f.read()
        with open("/home/pi/Desktop/MV1_firmware/logs/queue.txt", "w") as f:
            f.seek(0)
            f.truncate()
            fcntl.flock(f, fcntl.LOCK_UN)
        if contents != "" and contents != "\n":
            contents = contents.split("\n")
            for i in range(len(contents)-1):
                if contents[i] != "" and contents[i] != "\n":
                    message = contents[i].split(";")
                    msg_topic = message[0]
                    msg_payload = message[1]
                    print("Publishing message to topic '{}': {}".format(msg_topic, msg_payload))
                    message_json = json.dumps(msg_payload)
                    mqtt_connection.publish( topic=msg_topic, payload=message_json, qos=mqtt.QoS.AT_LEAST_ONCE)
                    sleep(0.2)
        with open("/home/pi/Desktop/MV1_firmware/logs/cache.txt", "w") as f:
            f.seek(0)
            f.truncate()
