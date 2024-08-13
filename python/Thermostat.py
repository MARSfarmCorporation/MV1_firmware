from Heater import Heater
from Exhaust_Fan import Exhaust_Fan
from Circulation_Fan import Circulation_Fan
from SHTC3 import *
from Trial_Util import Trial
from GPIO_Conf import ON, OFF
import time
from datetime import datetime

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

    def adjust(self):
        # Control code
        setpoint = self.get_Setpoint()
        temp = self.get_temp()
        print("Set", setpoint, "Temp", temp)
        self.cfan.on()  # Set circ fan state
        print("Circ_Fan: ON")

        if temp < setpoint:  # Measured temp is below setpoint
            self.heater.on()  # Turn on heater to raise temp
            print("Heater: On")
        else:  # Measured temp is above setpoint
            self.heater.off()  # Turn off heater to lower temp
            print("Heater: OFF")

            # Take multiple readings of the heater pin after attempting to turn it off
            self.check_heater_state(samples=100)

        # Exhaust fan control code
        if temp >= setpoint + 1:  # Measured temp is above setpoint by too much
            self.efan.on()  # Turn on exhaust fan
            print("Exhaust Fan ON")
        else:
            self.efan.off()  # Turn off fan
            print("Exhaust Fan OFF")

    def check_heater_state(self, samples=100, delay=0.01):
        # Check the state of the heater pin over a series of samples
        for i in range(samples):
            if self.heater.is_on():
                self.log_error("Heater unexpectedly on during off period.")
                break  # Log the error and exit early if an issue is detected
            time.sleep(delay)  # Small delay between readings

    def log_error(self, message):
        # Log an error message with a timestamp
        print(f"{datetime.now().isoformat()}: {message}\n")

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
