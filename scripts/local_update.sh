#!/bin/bash

echo "Attempting to pull GitHub"
cd /home/pi/Desktop/MV1_firmware

# Execute git pull and store its exit status
git pull
GIT_PULL_EXIT_STATUS=$?

# Check the exit status of git pull
if [ $GIT_PULL_EXIT_STATUS -ne 0 ]; then
    echo "Failed to pull from GitHub"
else
    echo "Pulled GitHub successfully"
fi

cd setup
crontab MV1_firmware_cron.txt
echo "Updated crontab successfully"

sleep 60
sudo reboot