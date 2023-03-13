'''
Author: Howard Webb - 11/2/2022
'''

from trial import trial as data
from time import time
from datetime import datetime



class Trial(object):
    
    def __init__(self):
        self.trial = data
        #print(data)
        self.trial_id = data['_id']
        self.trial_name = data['trial_name']
        self.device_id = data['device_id']
        self.device_name = data['device_name']
        self.model_name = data['model_name']
        self.recipe_id = data['recipe_id']
        self.recipe_name = data['recipe_name']
        self.start_date = self.trial['start_date']
        self.phases = self.trial['phases']
        self.phase_count = 0
        self.current_phase = self.get_current_phase() - 1

        #print(self.start_date)
    
    def get_current_phase(self):
        # Get the current phase from trial.py
        #print("Phases", self.phases)
        #print(self.start_date)
        self.phase_count = len(self.phases)
        for i in range(len(self.phases)):
            # If current time is greater than the start day of the phase, then it is saved
            # Loop is continued until current time is less than start day of phase
            if time() > (self.phases[i]['phase_start'] * 86400) + self.start_date:
                current_phase = self.phases[i]  # Save specific phase data
        
        return i

    def get_light_values(self, phase=None):
        # set the light schedule (cron times)
        # default to current phase
        if phase == None:
            phase = self.current_phase
            
        light_settings = self.phases[phase]['step'][3]['light_intensity']  # Store light settings are variable
        #print("Light", light_settings)

        # Look through light array and find most up to date light setting
        # NOTE: This only works if times are SORTED in ascending order in JSON
        lights = None
        current_time = datetime.now()

        
        for i in range(len(light_settings)):
            if ((current_time.hour*60) + current_time.minute) >= ((light_settings[i]['start_time'][0]*60) + light_settings[i]['start_time'][1]):
                lights = light_settings[i]['setting']  # Save temp if the current time is greater than time from array
        # break out inividual valuse fr, r, b, w
        return lights[0], lights[1], lights[2], lights[3]
    
    def get_setpoint(self, phase = None):
        # desired temperature
        if phase == None:
            phase = self.current_phase
            
        target_temp = None
        current_time = datetime.now()
        
        temp_settings = self.phases[phase]['step'][1]['temperature']  # Store light settings are variable
            
        for i in range(len(temp_settings)):

            if ((current_time.hour*60) + current_time.minute) >= ((temp_settings[i]['start_time'][0]*60) + temp_settings[i]['start_time'][1]):
                target_temp = temp_settings[i]['setting']  # Save temp if the current time is greater than time from array
            
        # get temperature setpoint for phase
        return target_temp

    def get_fan_setting(self, phase = None):
        # desired circulation fan setting
        if phase == None:
            phase = self.current_phase
            
        circ_setting = None
        current_time = datetime.now()
        
        circ_settings = self.phases[phase]['step'][0]['circulation_fan']  # Store light settings are variable
        for i in range(len(circ_settings)):

            if ((current_time.hour*60) + current_time.minute) >= ((circ_settings[i]['start_time'][0]*60) + circ_settings[i]['start_time'][1]):
                target_fan = circ_settings[i]['setting']  # Save setting if the current time is greater than time from array
        return target_fan
    
    def get_pump_setting(self, phase=None):
        # desired PUMP setting
        if phase == None:
            phase = self.current_phase
            
        pump_setting = 0
        current_time = datetime.now()
        pump_settings = self.phases[phase]['step'][2]['pump_amount']
        for i in range(len(pump_settings)):
                #Check array and see if it is time to dispense (could create problem, CHECK functionality)
            if ((current_time.hour*60) + current_time.minute) == ((pump_settings[i]['start_time'][0]*60) + pump_settings[i]['start_time'][1]): 
                pump_setting =  pump_settings[i]['setting']
        return pump_setting
    
    #---------------------------Test Functions -----------------------------
    def print_light(self):
        for i in range (self.phase_count):
            light_settings = self.phases[i]['step'][3]['light_intensity']
            for x in range(len(light_settings)):
                t = light_settings[x]['start_time']
                time = str(t[0])+':'+str(t[1])
                fr, r, b, w = light_settings[x]['setting']
                print("Phase:", i, "Time:", time, "F-Red", fr, "Red", r, "Blue", b, "White", w) 

    def print_setpoint(self):
        for i in range (self.phase_count):
            temp_settings = self.phases[i]['step'][1]['temperature']
            for x in range(len(temp_settings)):
                t = temp_settings[x]['start_time']
                time = str(t[0])+':'+str(t[1])
                f = temp_settings[x]['setting']
            
            s = self.get_setpoint(i)
            print("Phase:", i, "Setpoint", s) 

    def print_fan(self):
        for i in range (self.phase_count):
            fan_settings = self.phases[i]['step'][0]['circulation_fan']
            for x in range(len(fan_settings)):
                t = fan_settings[x]['start_time']
                time = str(t[0])+':'+str(t[1])
                f = fan_settings[x]['setting']
            print("Phase:", i, "Time:", time, "Fan Setting", f)
            
    def print_pump(self):
        for i in range (self.phase_count):
            pump_settings = self.phases[i]['step'][2]['pump_amount']
            for x in range(len(pump_settings)):
                t = pump_settings[x]['start_time']
                time = str(t[0])+':'+str(t[1])
                p = pump_settings[x]['setting']
                print("Phase:", i, "Time:", time, "Pump Setting", p)
     
    def pretty_print(self):
        # print structure in readable form
        import json
        json_object = self.trial
        json_format = json.dumps(json_object, indent=2)
        print(json_format)
    

def test():
    print("Trial Object Test")
    t = Trial()
    t.pretty_print()
    print('Trial Id:', t.trial_id)
    print('Trial Name:', t.trial_name)
    print('Device Id:', t.device_id)
    print('Device Name:', t.device_name)
    print('Recipe Id:', t.recipe_id)
    print('Recipe Name:', t.recipe_name)    
    print("Model Name:", t.model_name)
    #self.recipe = t.
    print("Start Date", t.start_date)
    print("Phase Count:",t.phase_count)
    phase = t.get_current_phase()
    print("Current Phase #", phase)
    #print("Current Phase", t.phases[phase])    
    #print("Light", t.phases[phase]['step'][3]['light_intensity'])
    fr, r, b, w = t.get_light_values()
    print("Light fr:", "R", r, "B", b, "W", w)
    target_temp = t.get_setpoint()
    print("Setpoint", target_temp)
    circ_fan = t.get_fan_setting()
    print("Circ_Fan", circ_fan)
    t.print_light()
    print("Fan Cycles")
    t.print_fan()
    print("Setpoints")
    t.print_setpoint()
    print("Pump Setting")
    t.print_pump()
    
    print("Done")
    
if __name__=="__main__":
    test()
