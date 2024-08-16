import subprocess
import time

def run_stress_test(script_name):
    process = subprocess.Popen(["python3", script_name])
    process.wait()  # Wait for the script to finish
    time.sleep(0.01)  # Short delay before restarting

if __name__ == "__main__":
    # List of stress test scripts
    scripts = [
        "Heater_Stress_NoSingleton.py", 
        "Pump_Stress_NoSingleton.py", 
        "Light_Stress_NoSingleton.py", 
        "Fan_Stress_NoSingleton.py"
    ]

    # Run each script in a separate process and loop them
    for script in scripts:
        subprocess.Popen(["python3", script])

    while True:
        # Wait a bit before restarting everything
        time.sleep(1)
        # Restart each script after it finishes
        for script in scripts:
            run_stress_test(script)
