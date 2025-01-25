import csv
import requests
import json
import pandas as pd
import numpy as np

# Load the CSV file and select the top 650 rows
data = pd.read_csv('uscities.csv')
top_650 = data.iloc[300:400] # first number isn't counted, so basically roww 301 to row 400

def get_data_for_coordinate(lat, lon):
    # National Weather Service
    response = requests.get(f'https://api.weather.gov/points/{lat},{lon}').json()

    gridX = response["properties"]["gridX"]
    gridY = response["properties"]["gridY"]
    cwa = response["properties"]["cwa"]

    response_hourly = requests.get(f'https://api.weather.gov/gridpoints/{cwa}/{gridX},{gridY}/forecast/hourly').json()

    elevation = response_hourly["properties"]["elevation"]["value"] # m
    temperature = response_hourly["properties"]["periods"][0]["temperature"] # deg F
    precipitationProbability = response_hourly["properties"]["periods"][0]["probabilityOfPrecipitation"]["value"] # %
    dewpoint = response_hourly["properties"]["periods"][0]["dewpoint"]["value"] # deg C
    humidity = response_hourly["properties"]["periods"][0]["relativeHumidity"]["value"] # %
    windSpeed = response_hourly["properties"]["periods"][0]["windSpeed"].split()[0] # mph

    # Time
    dateTime = requests.get(f'https://timeapi.io/api/time/current/coordinate?latitude={lat}&longitude={lon}').json()["dateTime"]

    # Meteomatics
    forestfireIndex = requests.get(
        f'https://api.meteomatics.com/{dateTime}Z/forest_fire_warning:idx/{lat},{lon}/json',
        auth=('tks_young_victor', 'U7vb9E5eAs')
    ).json()["data"][0]["coordinates"][0]["dates"][0]["value"]

    data = {
        "latitude": lat,
        "longitude": lon,
        "elevation": elevation,
        "temperature": temperature,
        "precipitationProbability": precipitationProbability,
        "dewpoint": dewpoint,
        "humidity": humidity,
        "windSpeed": windSpeed,
        "forestFireIndex": forestfireIndex
    }
    return data

# Output CSV file path
output_file = "Replicate 2 301-400 Data - Sheet1.csv"

# Automate data fetching and CSV writing
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Write header
    writer.writerow(["Latitude", "Longitude", "Elevation", "Temperature", 
                     "PrecipitationProbability", "Dewpoint", 
                     "Humidity", "WindSpeed", "ForestFireIndex"])
    
    # Fetch data for each coordinate and write to CSV
    for _, row in top_650.iterrows():
        lat = row['lat']
        lon = row['lng']
        data = get_data_for_coordinate(lat, lon)
        writer.writerow([
            data["latitude"],
            data["longitude"],
            data["elevation"],
            data["temperature"],
            data["precipitationProbability"],
            data["dewpoint"],
            data["humidity"],
            data["windSpeed"],
            data["forestFireIndex"]
        ])

print(f"Data written to {output_file}")