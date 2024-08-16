from Heater import Heater
from Exhaust_Fan import Exhaust_Fan
from Circulation_Fan import Circulation_Fan
from SHTC3 import *
from Trial_Util import Trial
from GPIO_Conf import ON, OFF
import time
from datetime import datetime
import os
from PigpioManager import PigpioManager
from WebSocketUtil import secure_database_write
from Sys_Conf import SERIAL_NUMBER

def restart_pigpiod():
    # Stop pigpiod
    os.system("sudo killall pigpiod")
    time.sleep(1)  # Wait for a moment to ensure pigpiod has stopped

    # Restart pigpiod with your specific settings
    os.system("sudo pigpiod -s1")  # Adjust the parameters as needed
    time.sleep(2)  # Give pigpiod time to fully initialize

    # You might also want to reinitialize your pigpio instance
    PigpioManager._instance = None  # Reset the singleton instance
    pi = PigpioManager().get_pi()  # Reconnect to pigpiod

class Thermostat(object):

    def __init__(self):
        self.tu = Trial()
        self.efan = Exhaust_Fan()
        self.cfan = Circulation_Fan()
        self.heater = Heater()

    def get_temp(self):
        s = SHTC3()
        temperature, humidity = s.get_tempF_humidity()
        return temperature

    def get_Setpoint(self):
        t_s = self.tu.get_setpoint()
        s = 90
        if int(t_s) < 90:
            s = t_s
        return s
    
    def log_overheat_event(self):
        try:
            topic = f"overheat/{SERIAL_NUMBER}"
            payload = {
                "timestamp": datetime.now().timestamp(),
                "message": f"Warning: {SERIAL_NUMBER} Overheat Event"
            }
            status = "Outbound - Unsent"
            secure_database_write(topic, json.dumps(payload), status)
        except Exception as e:
            print(f"Error logging overheat event: {e}")

    def adjust(self):
        # Control code
        setpoint = self.get_Setpoint()
        temp = self.get_temp()
        print("Set", setpoint, "Temp", temp)
        self.cfan.on()  # Set circ fan state
        print("Circ_Fan: ON")

        # Check if the temperature is too high and reboot if necessary
        if temp >= 100:
            print("Temperature exceeds 100°F. Logging event and rebooting system to prevent damage...")
            self.log_overheat_event()  # Log the overheat event to the database
            time.sleep(10)  # Wait for 10 seconds before rebooting
            os.system("sudo reboot")

        if temp < setpoint:  # Measured temp is below setpoint
            self.heater.on()  # Turn on heater to raise temp
            print("Heater: On")
            time.sleep(1)  # Wait for heater to turn on

            if not self.heater.is_on():
                print("Error: Heater did not turn on as expected!")
        else:  # Measured temp is above setpoint
            self.heater.off()  # Turn off heater to lower temp
            print("Heater: OFF")
            time.sleep(1)  # Wait for heater to turn off

            # Check if the heater actually turned off
            if self.heater.is_on():
                print("Error: Heater did not turn off as expected!")
                self.heater.reset_pin()  # Reset the pin

                # sleep for 0.1 seconds to allow the heater to turn off
                time.sleep(0.1)

                if self.heater.is_on():
                    print("Warning: Heater is still on after reset! Attempting to restart pigpiod...")
                    restart_pigpiod()  # Restart pigpiod if the issue persists
                    # Reattempt turning off the heater after restarting pigpiod
                    self.heater.off()
                    if self.heater.is_on():
                        print("Critical: Heater still on after pigpiod restart!")
                else:
                    print("Heater reset successfully, resuming normal operation...")

        # Exhaust fan control code
        if temp >= setpoint + 1:  # Measured temp is above setpoint by too much
            self.efan.on()  # Turn on exhaust fan
            print("Exhaust Fan ON")
        else:
            self.efan.off()  # Turn off fan
            print("Exhaust Fan OFF")

# Testing the thermostat
def test():
    print("Thermostat Test")
    t = Thermostat()
    print("Adjust")
    t.adjust()
    print(datetime.now().isoformat())
    print("Done")

if __name__ == "__main__":
    test()
