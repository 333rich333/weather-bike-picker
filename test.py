import json
import requests
import sys
import time

from data_handling import check_if_site_is_up, checkWindSpeed, request_data, checkRain, checkTemperature, find_today, \
        print_info


# Output: 3 Json files, this should only be run every 10-60 minutes at the earliest (minimize API calls)
def first_get_data():
    # Check if the site is up
    result = check_if_site_is_up()
    if isinstance(result, (int, float)):
        # Errored out, update json
        print("Error", result)
        return "Error: Cannot grab data"  # possibly replace with getting data from log?

    # Get data and put into .json's for local data handling
    request_data()


def third_print_data(config_data):
    print("hi")


def second_interpret_data():
    print("hi")
    # Import JSON: forecast & config
    with open('config.json', 'r') as json_file:
        config_data = json.load(json_file)
    with open('forecast.json', 'r') as json_file:
        forecast_data = json.load(json_file)
    with open('forecast_hourly.json', 'r') as json_file:
        forecast_hourly_data = json.load(json_file)
    if not find_today(forecast_data, forecast_hourly_data):
        return False

    # Load configs?

    # Check against rain, wind, weather for time specified
    config_data = checkWindSpeed(config_data, forecast_hourly_data)
    print("Done checking Wind")
    config_data = checkRain(config_data, forecast_hourly_data)
    print("Done checking Rain")
    config_data = checkTemperature(config_data, forecast_hourly_data)
    print("Done checking Temperature")

    # Check for rain, then for low wind speed, then high wind speed
    if config_data["rain"]["probabilityOfPrecipitation"] > config_data["user_configurations"][
            "probabilityOfPrecipitation"]:
        config_data["vehicle"] = config_data["vehicle_options"][2]  # car
    elif config_data["temperature"]["max_temp"] > config_data["user_configurations"]["heat_max"]:
        config_data["vehicle"] = config_data["vehicle_options"][2]  # car
    elif config_data["temperature"]["min_temp"] < config_data["user_configurations"]["cold_min"]:
        config_data["vehicle"] = config_data["vehicle_options"][2]  # car
    elif config_data["wind"]["max_speed"] < config_data["user_configurations"]["wind_grom_max"]:
        config_data["vehicle"] = config_data["vehicle_options"][0]  # grom
    elif config_data["wind"]["max_speed"] < config_data["user_configurations"]["wind_saber_max"]:
        config_data["vehicle"] = config_data["vehicle_options"][1]  # cruiser
    else:
        config_data["vehicle"] = config_data["vehicle_options"][2]  # car default

    # FINISHED
    with open('config2.json', 'w') as json_file:
        json.dump(config_data, json_file, indent=4)
        # print(data["user_configurations"])
    print("Wrote Data to", json_file.name)

    print_info(config_data)
    third_print_data(config_data)
    return True

first_get_data()
#second_interpret_data()


def killSwitch():
    time.sleep(0.5)
    print("Exiting Program...")
    sys.exit(0)
