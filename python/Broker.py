import sqlite3
import time
import json

# This function handles inbound messages and sorts them via their topic. It then updates the status in the database.
def process_inbound_message(cursor, id, topic, payload):
    try:
        # Takes 'trial' topics from the queue and writes the payload to trial.py
        if topic == 'trial':
            with open('trial.py', 'w') as file:
                file.write(payload)
            cursor.execute("UPDATE message_queue SET status = 'Inbound - Sorted' WHERE id = ?", (id,))
        else:
            # Handle other topics as needed
            pass
    except Exception as e:
        print(f"Error processing inbound message: {e}")
        cursor.execute("UPDATE message_queue SET status = 'Inbound - Unsortable' WHERE id = ?", (id,))

# This function handles outbound messages and sends them to the websocket server. It then updates the status in the database.
def process_outbound_message(cursor, id, topic, payload):
    try:
        # Create a Unix socket
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        
        # Connect to the Unix socket file
        client_socket.connect("/tmp/websocket_comms.sock")
        
        # Format the MQTT message
        message = json.dumps({"topic": topic, "payload": payload})
        
        # Send the message
        client_socket.sendall(message.encode())
        
        # Close the socket
        client_socket.close()
        
        # Update the status in the database
        cursor.execute("UPDATE mqtt_queue SET status = 'Outbound - Sent' WHERE id = ?", (id,))
    except Exception as e:
        print(f"Error sending outbound message: {e}")
        cursor.execute("UPDATE mqtt_queue SET status = 'Outbound - Unsendable' WHERE id = ?", (id,))

def main():
    conn = sqlite3.connect('message_queue.db')
    cursor = conn.cursor()

    while True:
        cursor.execute("SELECT id, topic, payload, status FROM message_queue WHERE status IN ('Inbound - Unsorted', 'Outbound - Unsent')")
        messages = cursor.fetchall()

        for message in messages:
            id, topic, payload, status = message
            if status == 'Inbound - Unsorted':
                process_inbound_message(topic, payload)
            elif status == 'Outbound - Unsent':
                process_outbound_message(topic, payload)
                cursor.execute("UPDATE message_queue SET status = 'Outbound - Sent' WHERE id = ?", (id,))

        conn.commit()
        time.sleep(0.25) # Sleep for 0.25 seconds to prevent excessive CPU usage

    conn.close()

if __name__ == "__main__":
    main()
