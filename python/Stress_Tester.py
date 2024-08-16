import subprocess
import time

def run_stress_test(script_name):
    process = subprocess.Popen(["python3", script_name])
    process.wait()  # Wait for the script to finish
    time.sleep(0.01)  # Short delay before restarting

if __name__ == "__main__":
    # List of stress test scripts
    scripts = ["Heater_Stress.py", "Pump_Stress.py", "Light_Stress.py", "Fan_Stress.py"]

    while True:
        # Start and wait for each script to finish
        for script in scripts:
            run_stress_test(script)
        
        # Optional: Wait a bit before restarting everything
        time.sleep(1)
