import Fan
import Heater
from SI7021 import *

fan1 = Fan.Fan(16) #Create circulation fan 
heater = Heater.Heater(5)
fan1.setState(1) #Leave on forever

set_point = 26.6 #Given in C
hysteresis = 0.5

si=SI7021()

while True:
    temp = si.get_tempC()
    print(temp, "C")

    if ( (temp < setpoint + hysteresis) and (hysteresis > 0) ): #Measured temp is below setpoint
        heater.setState(1) #Turn on heater to raise temp   

    if ( (temp > setpoint + hysteresis) and (hysteresis > 0) ): #Measured temp is below setpoint
        #Hysteresis is present to prevent fast switching of heater
        #Once heater has been turned on, the setpoint needs to be "moved"
        hysteresis = hysteresis * -1
        heater.setState(0) #Turn off heater to lower temp
         
    if ( (temp > setpoint + hysteresis) and (hysteresis < 0) ): #Measured temp is above setpoint
        heater.setState(0) #Turn off heater to lower temp

    if ( (temp < setpoint + hysteresis) and (hysteresis < 0) ): #Measured temp is below setpoint
        #Hysteresis is present to prevent fast switching of heater
        #Once heater has been turned on, the setpoint needs to be "moved"
        hysteresis = hysteresis * -1
        heater.setState(1) #Turn on heater to raise temp  
