'''
# created on 07.20.2021 by Peter Webb in Sprint 5 of Summer 2021
# script developed to test subscribing to MQTT topics and publishing JSON

Author: Peter Webb - 07.20.2021
Modified by: Peter Webb - 09.20.2022
Modified by: Peter Webb - 11.21.2022
'''
import paho.mqtt.client as mqttClient
import Lights
import time
from datetime import datetime
import ssl
import trial
from Sys_Conf import DEVICE_ID

# Import dictionary data
data = trial.trial

# REPLACED with hardcoded device for provisioning in production
#define local device which should be passed in eventually
#deviceID = data['device_id']
deviceID = DEVICE_ID

context = ssl.create_default_context()
# create connection
Connected = False
broker_address = "b-7b51011f-b159-48b9-ba5b-b88b236dec5d-1.mq.us-east-2.amazonaws.com"  # No ssl://
port = 8883
user = "RaspberryPi"
password = "marsfarmtesting"

# define topic
msg_root_topic = "marsfarm"
subscribe_topic = (msg_root_topic + "/" + deviceID)
ct = datetime.now().strftime('%Y-%m-%d_%H%M')

# print(subscribe_topic)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker at: " + ct)
        global Connected  # Use global variable
        Connected = True  # Signal connection
        client.subscribe(subscribe_topic)
        print("Subscribed to topic: " + subscribe_topic)
    else:
        print("Connection failed")


def on_message(client, userdata, msg):
    #    print(msg.topic+" "+str(msg.payload))
    if msg.topic == subscribe_topic:
        output = msg.payload
        print(output)
        with open("/home/pi/Desktop/MV1_firmware/python/trial.py", "w") as f:
            f.write(output.decode('utf-8'))
            f.close()
            print("Done!")
    else:
        print("not this device")

try:
    print("Client Created")
    client = mqttClient.Client("MV1")  # create new instance
    client.username_pw_set(user, password=password)  # set username and password
    client.on_connect = on_connect
    print("Initialize connect")
    client.on_message = on_message
    print("Initialize message")
    client.tls_set_context(context=context)
    client.connect(broker_address, port=port)
    client.loop_start()

    while Connected != True:
        time.sleep(0.1)

    # Loop forever so script doesn't end
    while True:
        time.sleep(60)

except Exception as e:
    print(e)
    # Record previous light settings
    #farred = pi.get_PWM_dutycycle(26)
    #red = pi.get_PWM_dutycycle(5)
    #blue = pi.get_PWM_dutycycle(13)
    #white = pi.get_PWM_dutycycle(19)

    # Turn on red light at 100% to signify error
    #lights.customMode(0, 255, 0, 0)
    #sleep(10)
    # Return light to previous settings
    #lights.customMode(farred, red, blue, white)
