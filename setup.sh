#!/bin/bash
#ONLY RUN THIS FILE ONCE
#Get the project and dependencies
git clone https://github.com/333rich333/weather-bike-picker.git
apt update
apt install python3
apt install ptyhon3-pip
pip3 install eel
cd weather-bike-picker
#Add the service to the os.
cp bootup/weather-bike-picker.service /etc/systemd/system/

#Enble the service
systemctl enable weather-bike-picker.service