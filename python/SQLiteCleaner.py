import sqlite3
import os

def delete_sorted_and_sent_messages():
    # Use the full path to the database
    db_path = os.path.join(os.path.dirname(__file__), 'message_queue.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM message_queue
    WHERE status IN ('Inbound - Sorted', 'Outbound - Sent')
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    delete_sorted_and_sent_messages()
