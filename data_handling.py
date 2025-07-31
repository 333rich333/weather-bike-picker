import json
import requests
import datetime


def find_today(forecast_data, forecast_hourly_data):
    today_str = datetime.date.today().isoformat()
    periods = forecast_hourly_data['properties'].get("periods", [])
    for period in periods:
        date, time_str, time_digits = parse_datetime_iso8601(period['startTime'])
        # Convert time to integer for easy comparison (HHMM)
        # We only need HHMM part, so slice first 4 digits
        if date == today_str:
            return True
        # continue through
    # end for loop
    return False


def print_info(config_data):
    print("Rain Probability:", config_data["rain"]["probabilityOfPrecipitation"])
    print("Max Temp:", config_data["temperature"]["max_temp"])
    print("Min Temp:", config_data["temperature"]["min_temp"])
    print("Max Wind Speed:", config_data["wind"]["max_speed"])
    print("Min Wind Speed:", config_data["wind"]["min_speed"])
    print("Vehicle of Choice:", config_data["vehicle"])


def parse_datetime_iso8601(dt_string):  # chatgpt
    # "2025-07-27T19:00:00-07:00"
    if "T" in dt_string:
        date_part, time_zone_part = dt_string.split("T")
        if "-" in time_zone_part[6:]:  # Check if timezone is present
            time_part, tz_offset = time_zone_part[:8], time_zone_part[8:]
        elif "+" in time_zone_part[6:]:
            time_part, tz_offset = time_zone_part[:8], time_zone_part[8:]
        else:
            time_part = time_zone_part
            tz_offset = None
        return date_part, time_part, tz_offset
    else:
        return None


def parse_speed_range(text, min_speed=None, max_speed=None):  # Chatgpt
    # format: "10 mph"
    speed = int(text.split()[0])
    if min_speed is None or speed < min_speed:
        min_speed = speed
    if max_speed is None or speed > max_speed:
        max_speed = speed
    return min_speed, max_speed


def parse_temp_range(text, min_temp=None, max_temp=None):  # Chatgpt
    # format: "10 mph"
    speed = int(text)
    if min_temp is None or speed < min_temp:
        min_temp = speed
    if max_temp is None or speed > max_temp:
        max_temp = speed
    return min_temp, max_temp


def check_if_site_is_up():  # chatgpt
    try:
        site_url = "https://api.weather.gov"
        fallback_url = "https://www.google.com"
        # Step 1: Try to connect to the target site
        response = requests.get(site_url, timeout=1)
        if response.status_code == 200:
            return (f"{site_url} is up ✅")
        else:
            return f"2: {site_url} returned status code {response.status_code} ⚠️"
    except requests.ConnectionError:
        # Step 2: Fallback check to see if user has internet
        try:
            requests.get(fallback_url, timeout=1)
            return f"404: {site_url} appears to be down ❌ (but your internet is working)"
        except requests.ConnectionError:
            return "1: You appear to have no internet connection ❌"
    except requests.Timeout:
        return f"3: {site_url} timed out ⏳"
    except Exception as e:
        return f"Unexpected error: {e}"


# result = check_if_site_is_up()
# print(result)

def request_data():
    ip_info = requests.get(f"https://ipinfo.io/json")
    ip_info.raise_for_status()
    location_data = ip_info.json()

    # Extract the "loc" field (latitude,longitude)
    loc = location_data["loc"]
    weather_url = f"https://api.weather.gov/points/{loc}"
    r = requests.get(weather_url)
    r.raise_for_status()
    pt = r.json()

    forecast_url = pt["properties"]["forecast"]
    hourly_url = pt["properties"]["forecastHourly"]
    # Step 2: get daily/period forecast
    f = requests.get(forecast_url)
    forecast = f.json()
    f2 = requests.get(hourly_url)
    forecast_hour = f2.json()

    with open('forecast_url.json', 'w') as file:
        json.dump(pt, file, indent=4)
    with open('forecast.json', 'w') as file:
        json.dump(forecast, file, indent=4)
    with open('forecast_hourly.json', 'w') as file:
        json.dump(forecast_hour, file, indent=4)

    periods = forecast["properties"]["periods"]
    for p in periods[:5]:
        print(p["name"], p["startTime"], p["temperature"], p["shortForecast"])


def checkWindSpeed(config_data, forecast_hourly):
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

    # Cycle Through hourly data - Chatgpt
    periods = forecast_hourly['properties'].get("periods", [])
    min_speed, max_speed = parse_speed_range(periods[0]["windSpeed"])
    time_start = config_data["user_configurations"]["time_start"]
    time_end = config_data["user_configurations"]["time_end"]
    for period in periods:
        todays_date, time_str, time_digits = parse_datetime_iso8601(period['startTime'])
        # Convert time to integer for easy comparison (HHMM)
        # We only need HHMM part, so slice first 4 digits
        time_hhmm = int(time_str.replace(":", "")[:4]) if time_str else 0
        if time_hhmm == 0:  # Grab weather data until midnight
            break
        # Only update times specified by user configuration
        if time_start <= time_hhmm <= time_end:
            min_speed, max_speed = parse_speed_range(period['windSpeed'], min_speed, max_speed)
        # print(time_hhmm, min_speed, max_speed)
    # end for loop
    config_data["wind"]["min_speed"] = min_speed
    config_data["wind"]["max_speed"] = max_speed

    # Check the speed and assign the appropriate value
    if max_speed == 0:
        config_data["wind"]["intensity"] = config_data["wind"]["condition"][0]
    elif 1 <= max_speed <= 7:
        config_data["wind"]["intensity"] = config_data["wind"]["condition"][1]
    elif 8 <= max_speed <= 12:
        config_data["wind"]["intensity"] = config_data["wind"]["condition"][2]
    elif 13 <= max_speed <= 18:
        config_data["wind"]["intensity"] = config_data["wind"]["condition"][3]
    elif 19 <= max_speed <= 38:
        config_data["wind"]["intensity"] = config_data["wind"]["condition"][4]
    elif 39 <= max_speed:
        config_data["wind"]["intensity"] = config_data["wind"]["condition"][5]
    else:
        config_data["wind"]["intensity"] = config_data["wind"]["condition"][6]

    return config_data


# checkWindSpeed()

def checkRain(config_data, forecast_hourly):
    # Check if the provided rain_option is in the available options?
    rain_config = config_data["user_configurations"]["rain_max"]

    # Cycle Through hourly data - Chatgpt
    periods = forecast_hourly['properties'].get("periods", [])
    time_start = config_data["user_configurations"]["time_start"]
    time_end = config_data["user_configurations"]["time_end"]
    rain_chance = 0
    for period in periods:
        todays_date, time_str, time_digits = parse_datetime_iso8601(period['startTime'])
        # Convert time to integer for easy comparison (HHMM)
        # We only need HHMM part, so slice first 4 digits
        time_hhmm = int(time_str.replace(":", "")[:4]) if time_str else 0
        if time_hhmm == 0:  # Grab weather data until midnight
            break
        # Only update times specified by user configuration
        if time_start <= time_hhmm <= time_end:
            # min_speed, max_speed = parse_speed_range(period['windSpeed'], min_speed, max_speed)
            forecast_rain = int(period['probabilityOfPrecipitation']['value'])
            if forecast_rain > rain_chance:  # update rain_chance for config file
                rain_chance = forecast_rain
        # print(time_hhmm,rain_chance)
    # end for loop
    config_data["rain"]["probabilityOfPrecipitation"] = rain_chance
    return config_data


def checkTemperature(config_data, forecast_hourly):
    time_start = config_data["user_configurations"]["time_start"]
    time_end = config_data["user_configurations"]["time_end"]
    min_temp = None
    max_temp = None

    periods = forecast_hourly['properties'].get("periods", [])
    for period in periods:
        todays_date, time_str, time_digits = parse_datetime_iso8601(period['startTime'])
        # Convert time to integer for easy comparison (HHMM)
        # We only need HHMM part, so slice first 4 digits
        time_hhmm = int(time_str.replace(":", "")[:4]) if time_str else 0
        if time_hhmm == 0:  # Grab weather data until midnight
            break
        # Only update times specified by user configuration
        if time_start <= time_hhmm <= time_end:
            min_temp, max_temp = parse_temp_range(period['temperature'], min_temp, max_temp)
        # print(time_hhmm, min_temp, max_temp)
    # end for loop
    config_data["temperature"]["min_temp"] = min_temp
    config_data["temperature"]["max_temp"] = max_temp
    config_data["temperature"]["temperatureUnit"] = period['temperatureUnit']

    return config_data
