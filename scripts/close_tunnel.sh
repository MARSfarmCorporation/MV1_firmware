#!/bin/bash

# Find the PID of the localproxy process
PID=$(pgrep localproxy)

# Check if the process was found
if [ -z "$PID" ]; then
  echo "No localproxy process found."
  exit 1
fi

# Gracefully kill the process
echo "Goodbye!"
sleep 2
kill $PID