#!/bin/bash

# Define the paths to the database file and the Python script
DATABASE_FILE="/home/pi/Desktop/MV1_firmware/python/message_queue.db"
PYTHON_SCRIPT="/home/pi/Desktop/MV1_firmware/python/Create_Database.py"

# Check if the SQLite server file exists
if [ -f "$DATABASE_FILE" ]; then
    # Attempt to remove the SQLite server file
    rm "$DATABASE_FILE"
    
    # Check if the file removal was successful
    if [ $? -eq 0 ]; then
        echo "SQLite server removed successfully."
        
        # Run the Python script with python3
        python3 "$PYTHON_SCRIPT"
        
        # Check if the Python script ran successfully
        if [ $? -eq 0 ]; then
            echo "Database created successfully."
        else
            echo "Failed to run the Python script."
            exit 1
        fi
    else
        echo "Failed to remove the SQLite server."
        exit 1
    fi
else
    echo "SQLite server file does not exist. Creating a new database."
    
    # Run the Python script with python3
    python3 "$PYTHON_SCRIPT"
    
    # Check if the Python script ran successfully
    if [ $? -eq 0 ]; then
        echo "Database created successfully."
    else
        echo "Failed to run the Python script."
        exit 1
    fi
fi

# If we got this far, everything was successful
exit 0
