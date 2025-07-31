from flask import Flask

app = Flask(__name__)
import requests
import json

#sudo apt install python3, python3-pip, python3-requests, python3-flask

@app.route('/')
def get_weather():
    url = ""
    response = json.loads(requests.request("GET",url).text)
    return response
