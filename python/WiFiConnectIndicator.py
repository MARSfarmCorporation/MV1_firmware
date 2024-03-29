# This script will blink the LED when WiFi Connect needs to be launched due to a network connection failure.
from Lights import Light

def wifi_connect_sequence():
    # Create an instance of the Light class
    light = Light()

    # Call the wifi_connect_launch method to blink the lights
    # as an indication that the WiFi connection process is being initiated
    light.wifi_connect_launch()

if __name__ == "__main__":
    # Execute the WiFi connection sequence
    wifi_connect_sequence()