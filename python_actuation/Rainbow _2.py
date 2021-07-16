import Fan
import Pump
import Lights

lights = Lights.Light(26,5,6,13,19)
fan1 = Fan.Fan(16)
fan2 = Fan.Fan(20)
pump = Pump.Pump(24,23)
import time

lights.customMode(0,0,0,0,0)

i = 0

while True:
    lights.customMode( 0, abs(100 - (i%200)), abs(100 - (((.2*i)+61)%200)), abs(100 - (((.3*i)+108)%200)), abs(100 - (((.4*i)+163)%200)))
    time.sleep(0.05)
    i = i + 1
    
    if (i%200 > 100):
        fan1.setState(1)
        fan2.setState(0)
    else:
        fan1.setState(0)
        fan2.setState(1)