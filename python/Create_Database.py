import sqlite3

def create_database():
    conn = sqlite3.connect('message_queue.db')
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE message_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        payload TEXT,
        status TEXT CHECK(status IN (
                    'Inbound - Unsorted', 
                    'Inbound - Sorted',
                    'Outbound - Unsent',
                    'Outbound - Pending',
                    'Outbound - Pending Connection Restore',
                    'Outbound - Sent',
                    'Inbound - Unsortable',
                    'Inbound - Unsortable - Job Error 1', 
                    'Inbound - Unsortable - Job Error 2',
                    'Inbound - Unsortable - Job Error 3',
                    'Inbound - Unsortable - Job Error Unknown',
                    'Inbound - Unsortable - Timeout',
                    'Inbound - Unsortable - Unknown',
                    'Inbound - Unsortable - Unrecognized Topic'
                   )),
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("CREATE INDEX idx_status ON message_queue(status);")
    cursor.execute("CREATE INDEX idx_topic ON message_queue(topic);")

    conn.commit()
    conn.close()

# Inbound - Unsorted: Message has been received from the MQTT broker but has not yet been processed
# Inbound - Sorted: Message has been received from the MQTT broker and has been processed
# Outbound - Unsent: Message has been added to the message queue but has not yet been sent to the websocket server
# Outbound - Pending: Message has been sent to the websocket server but has not yet been acknowledged
# Outbound - Pending Connection Restore: Message has been sent to the websocket server but was unable to send due to a connection error. The message will be resent when the connection is restored
# Outbound - Sent: Message has been sent to the websocket server and has been acknowledged
# Inbound - Unsortable: Message has been received from the MQTT broker but cannot be processed
# Inbound - Unsortable - Job Error 1: See 'Job_Agent.py' for more information
# Inbound - Unsortable - Job Error 2: See 'Job_Agent.py' for more information
# Inbound - Unsortable - Job Error 3: See 'Job_Agent.py' for more information
# Inbound - Unsortable - Job Error Unknown: See 'Job_Agent.py' for more information
# Inbound - Unsortable - Timeout: See 'Job_Agent.py' for more information
# Inbound - Unsortable - Unknown: Catch-all error for messages that fail unexpectedly
# Inbound - Unsortable - Unrecognized Topic: Message has been received from the MQTT broker but the topic is not recognized

if __name__ == "__main__":
    create_database()
