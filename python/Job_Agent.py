import sys
import json
import socket
import subprocess
from Sys_Conf import SERIAL_NUMBER
from WebSocketUtil import aws_enqueue

###########################################################################################################################
# SCRIPT PATHS
###########################################################################################################################

ota_update_script_path = "/home/pi/Desktop/MV1_firmware/scripts/ota_update.sh"

###########################################################################################################################
# FUNCTIONS
###########################################################################################################################

# This function closes the socket gracefully and exits the program
def exit(job_socket):
    job_socket.close()
    sys.exit() # Exit the program when the job succeeds, sends a return code of 0 to the broker

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

        # write the payload to Job_Agent_Log.txt, on a new line each time (make sure the file is there), with the prefix "Job_Agent.py: "
        with open('Job_Agent_Log.txt', 'a') as file:
            file.write(f"Job_Agent.py: {payload}\n")

        # Parse the payload JSON and extract the job details
        payload_json = json.loads(payload)

        with open('Job_Agent_Log.txt', 'a') as file:
            file.write(f"Job_Agent.py: payload_json: {payload_json}\n")

        job_details = payload_json['execution']
        jobID = job_details['jobId']

        job_name = job_details['jobDocument']['steps'][0]['action']['name']

        with open('Job_Agent_Log.txt', 'a') as file:
            file.write(f"Job_Agent.py: job_name: {job_name}\n")

        # Connect to the job_socket as a client
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as job_socket:
            job_socket.connect("/tmp/job_socket.sock")

            # Send the jobID to the job_socket to be set as a variable for the subscriber
            jobID_message = {
                "type": "jobID",
                "jobID": jobID
            }
            jobID_message_json = json.dumps(jobID_message)

            with open('Job_Agent_Log.txt', 'a') as file:
                file.write(f"Job_Agent.py: jobID_message_json: {jobID_message_json}\n")

            job_socket.sendall((jobID_message_json + '\n').encode())
        
            # Execute the job
            if job_name == "OTA_Update":
                # Execute the shell script
                try:
                    result = subprocess.run([ota_update_script_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    print(f"Script output: {result.stdout.decode('utf-8')}")
                except subprocess.CalledProcessError as e:
                    print(f"Error executing the script: {e.stderr.decode('utf-8')}")
                    exit_fail(job_socket) # Exit the program when the job fails, sends a return code of 3 to the broker
            else:
                print(f"Unknown job name: {job_name}")
                exit(job_socket)

            with open('Job_Agent_Log.txt', 'a') as file:
                file.write(f"Job_Agent.py: result: {result}\n")

            # Format the job status to be sent to the job_socket
            if result.returncode == 0:
                job_status = "SUCCEEDED"
                job_result = {
                    "status": job_status
                }
                with open('Job_Agent_Log.txt', 'a') as file:
                    file.write(f"Job_Agent.py: job_result_success: {job_result}\n")
            else:
                job_status = "FAILED"
                job_result = {
                    "status": job_status,
                    "statusDetails": {
                        "reason": "Script execution failed",
                        "message": result.stderr.decode('utf-8')
                    }
                }
                with open('Job_Agent_Log.txt', 'a') as file:
                    file.write(f"Job_Agent.py: job_result_failure: {job_result}\n")
            
            # Send the job status to the job_socket, formatted as a JSON string with a topic and a payload
            publish_message = {
                "type": "publish",
                "topic": f"$aws/things/{SERIAL_NUMBER}/jobs/{jobID}/update",
                "payload": json.dumps(job_result)
            }
            job_socket.sendall((json.dumps(publish_message) + '\n').encode())
            print(f"Job status sent to job_socket: {job_result}")

            #this will try to send the job status to the broker via the message_queue.db route
            try:
                aws_enqueue(publish_message['topic'], job_result)
            except Exception as e:
                print(f"Error logging job status: {e}")
                with open('Job_Agent_Log.txt', 'a') as file:
                    file.write(f"Job_Agent.py: Failed to enqueue: {e}\n")

            # Close the socket and exit the program, sends a return code of 0 to the broker
            exit(job_socket)

    # Handle exceptions    
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON payload: {e}")
        with open('Job_Agent_Log.txt', 'a') as file:
            file.write(f"Job_Agent.py: Error Code 1 {e}\n")
        sys.exit(1)

    except socket.error as e:
        print(f"Error connecting to job_socket: {e}")
        with open('Job_Agent_Log.txt', 'a') as file:
            file.write(f"Job_Agent.py: Error Code 2 {e}\n")
        sys.exit(2)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        with open('Job_Agent_Log.txt', 'a') as file:
            file.write(f"Job_Agent.py: Error Code 4 {e}\n")
        sys.exit(4)  # or another unique code

if __name__ == "__main__":
        main()
