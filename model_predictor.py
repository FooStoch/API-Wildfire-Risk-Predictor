import requests
import json
import numpy as np
from keras.models import load_model
from sklearn.preprocessing import StandardScaler
import joblib

lat = input()
lon = input()

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

print(elevation, temperature, precipitationProbability, dewpoint, humidity, windSpeed)

# Time
dateTime = requests.get(f'https://timeapi.io/api/time/current/coordinate?latitude={lat}&longitude={lon}').json()["dateTime"]

print(dateTime)

# Meteomatics
forestfireIndex = requests.get(
    f'https://api.meteomatics.com/{dateTime}Z/forest_fire_warning:idx/{lat},{lon}/json',
    auth=('tks_young_victor', 'U7vb9E5eAs')
).json()["data"][0]["coordinates"][0]["dates"][0]["value"]

print(forestfireIndex)

model = load_model('wildfire_risk_model.keras')

scaler = joblib.load('scaler.pkl')

inputs = np.array([[dewpoint, elevation, humidity, lat, lon, precipitationProbability, temperature, windSpeed]])

inputs = scaler.transform(inputs)

prediction = model.predict(inputs)
predictedIndex = prediction[0][0]  # Return the predicted value

print(f"Predicted ForestFireIndex: {predictedIndex:.4f}")