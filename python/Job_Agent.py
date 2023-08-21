import sys
import json
import socket
import subprocess
from Sys_Conf import SERIAL_NUMBER

###########################################################################################################################
# SCRIPT PATHS
###########################################################################################################################

ota_update_script_path = "../scripts/ota_update.sh"

###########################################################################################################################
# FUNCTIONS
###########################################################################################################################

# This function closes the socket gracefully and exits the program
def exit(job_socket):
    job_socket.close()
    sys.exit()

# This function closes the socket and exits the program with a return code of 3 to the broker
def exit_fail(job_socket):
    job_socket.close()
    sys.exit(3)

###########################################################################################################################
# MAIN FUNCTION AND SOCKET CLIENT
###########################################################################################################################

def main():
    try:    
        # Receive the message payload from the command-line arguments
        payload = sys.argv[1]

        # Parse the payload JSON and extract the job details
        payload_json = json.loads(payload)
        job_details = payload_json['execution']
        jobID = job_details['jobId']
        job_status = job_details['status']
        job_document = job_details['jobDocument']
        job_steps = job_document['steps']
        job_action = job_steps[0]['action']
        job_name = job_action['name']

        # Connect to the job_socket as a client
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as job_socket:
            job_socket.connect("/tmp/job_socket.sock")

            # Send the jobID to the job_socket to be set as a variable for the subscriber
            jobID_message = {
                "type": "jobID",
                "jobID": jobID
            }
            job_socket.sendall(jobID_message.encode())
        
            # Execute the job
            if job_name == "OTA_Update":
                # Execute the shell script
                try:
                    result = subprocess.run([ota_update_script_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    print(f"Script output: {result.stdout.decode('utf-8')}")
                except subprocess.CalledProcessError as e:
                    print(f"Error executing the script: {e.stderr.decode('utf-8')}")
                    exit_fail(job_socket)
            else:
                print(f"Unknown job name: {job_name}")
                exit(job_socket)

            # Format the job status to be sent to the job_socket
            if result.returncode == 0:
                job_status = "SUCCEEDED"
                job_result = {
                    "status": job_status
                }
            else:
                job_status = "FAILED"
                job_result = {
                    "status": job_status,
                    "statusDetails": {
                        "reason": "Script execution failed",
                        "message": result.stderr.decode('utf-8')
                    }
                }
            
            # Send the job status to the job_socket, formatted as a JSON string with a topic and a payload
            publish_message = {
                "type": "publish",
                "topic": f"$aws/things/{SERIAL_NUMBER}/jobs/{jobID}/update/",
                "payload": json.dumps(job_result)
            }
            job_socket.sendall(json.dumps(publish_message).encode())
            print(f"Job status sent to job_socket: {job_result}")

            # Close the socket and exit the program, sends a return code of 0 to the broker
            exit(job_socket)

    # Handle exceptions    
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON payload: {e}")
        sys.exit(1)

    except socket.error as e:
        print(f"Error connecting to job_socket: {e}")
        sys.exit(2)

if __name__ == "__main__":
        main()
