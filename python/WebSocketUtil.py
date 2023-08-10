from datetime import datetime
from dateutil import parser
import fcntl
from Trial_Util import Trial

def enqueue(name, value, unit, observation_date, model):
    with open("/home/pi/Desktop/MV1_firmware/logs/queue.txt", "a") as f:
       t = Trial()
       date = parser.parse(datetime.fromtimestamp(observation_date).isoformat())
       day = abs((datetime.fromtimestamp(t.start_date)-datetime.fromtimestamp(observation_date)).days)
       week = abs(int(day/7))
       formatted_date = datetime.fromtimestamp(observation_date)
       formatted_start = datetime.fromtimestamp(t.start_date).strftime("%Y-%m-%d %H:%M:%S")
       fcntl.flock(f, fcntl.LOCK_EX)
       f.write("devicedata;" + f'{{"timestamp": "{observation_date}", "observation_date": "{formatted_date}", "attribute": "{name}", "value": {value}, "unit": "{unit}", "trial_id": "{t.trial_id}", "trial_name": "{t.trial_name}", "trial_start_date": "{formatted_start}", "day_number": {day}, "week_number": {week}, "model_name": "{model}"}}' + "\n")
       fcntl.flock(f, fcntl.LOCK_UN)