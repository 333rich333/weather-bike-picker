#Get updates
git pull
#Ensure service is enabled & start server
systemctl enable weather-bike-picker.service
python3 weather_eel.py
