from datetime import datetime
from dateutil import parser
from Trial_Util import Trial
import json

def enqueue(name, value, unit, observation_date, model):
    t = Trial()
    date = parser.parse(datetime.fromtimestamp(observation_date).isoformat())
    day = abs((datetime.fromtimestamp(t.start_date) - datetime.fromtimestamp(observation_date)).days)
    week = abs(int(day / 7))
    formatted_date = datetime.fromtimestamp(observation_date).isoformat() + "Z"
    formatted_start = datetime.fromtimestamp(t.start_date).strftime("%Y-%m-%d %H:%M:%S")

    payload = {
        "timestamp": observation_date,
        "observation_date": formatted_date,
        "attribute": name,
        "value": value,
        "unit": unit,
        "trial_id": t.trial_id,
        "trial_name": t.trial_name,
        "trial_start_date": formatted_start,
        "day_number": day,
        "week_number": week,
        "model_name": model
    }

    return json.dumps(payload)
