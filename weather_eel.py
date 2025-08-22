import eel
import random
import json

# Set web files folder and optionally specify which file types to check for eel.expose()
#   *Default allowed_extensions are: ['.js', '.html', '.txt', '.htm', '.xhtml']
eel.init('web', allowed_extensions=['.js', '.html'])

@eel.expose                         # Expose this function to Javascript
def say_hello_py():
    print('Hello from Python')

@eel.expose
def get_time():
    timestamp = dt.now()
    eel.addText("The time is now {}".format(timestamp.strftime("%I:%M:%S %p")))

numbers = 0,1,2,3,4,5

@eel.expose
def infoget(text):
    answer = sorted([int(num) for num in text.split(",")])
    eel.showAnswers(answer)

#say_hello_py('Python World!')

@eel.expose
def checkWindSpeed():
    with open('config.json', 'r') as json_file:
        # print(json_file.read())
        data = json.load(json_file)
        # "wind": {
        # "speed": 15,
        # "unit": "mph",
        # "options": [
        #   "none", //0
        #   "light", //0-7
        #   "gentle", //8-12
        #   "moderate", //13-18
        #   "strong", //19-38
        #   "storm" //39+

    wind = data["wind"]["speed"]
    # Check if the provided rain_option is in the available options
    if wind == 0:
        data["wind"]["intensity"] = data["wind"]["condition"][0]
    elif 1 <= wind <= 7:
        data["wind"]["intensity"] = data["wind"]["condition"][1]
    elif 8 <= wind <= 12:
        data["wind"]["intensity"] = data["wind"]["condition"][2]
    elif 13 <= wind <= 18:
        data["wind"]["intensity"] = data["wind"]["condition"][3]
    elif 19 <= wind <= 38:
        data["wind"]["intensity"] = data["wind"]["condition"][4]
    elif 39 <= wind:
        data["wind"]["intensity"] = data["wind"]["condition"][5]
    else:
        data["wind"]["intensity"] = data["wind"]["condition"][6]

    with open('config2.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
        # print(data["user_configurations"])

eel.init('www')
eel.start('weather_eel.html', mode='default')             # Start (this blocks and enters loop)

