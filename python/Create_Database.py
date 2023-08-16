import sqlite3

def create_database():
    conn = sqlite3.connect('message_queue.db')
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE message_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        payload TEXT,
        status TEXT CHECK(status IN ('Inbound - Unsorted', 'Inbound - Sorted', 'Outbound - Unsent', 'Outbound - Sent', 'Inbound - Unsortable')),
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("CREATE INDEX idx_status ON message_queue(status);")
    cursor.execute("CREATE INDEX idx_topic ON message_queue(topic);")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
