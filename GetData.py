import requests
import json

lat = input()
long = input()

response = requests.get(f'https://api.weather.gov/points/{lat},{long}').json()

#response_pretty = json.dumps(response, indent=2)
#print(response_pretty)

gridX = response['properties']['gridX']
gridY = response['properties']['gridY']
CWA = response['properties']['cwa']

response2 = requests.get(f'https://api.weather.gov/gridpoints/{CWA}/{gridX},{gridY}/forecast/hourly').json()

#response_pretty2 = json.dumps(response2, indent=2)
#print(response_pretty2)

elevation = response2['properties']['elevation']['value']
temp = response2['properties']['periods'][0]['temperature']
probOfPrec = response2['properties']['periods'][0]['probabilityOfPrecipitation']['value']
dewPoint = response2['properties']['periods'][0]['dewpoint']['value']
hum = response2['properties']['periods'][0]['relativeHumidity']['value']
windSpeed = response2['properties']['periods'][0]['windSpeed'].split()[0]

response3 = requests.get(f'https://timeapi.io/api/time/current/coordinate?latitude={lat}&longitude={long}').json()

time = response3['dateTime']

response4 = requests.get(f'https://api.meteomatics.com/{time}Z/forest_fire_warning:idx/{lat},{long}/json', auth=('tks_young_victor', 'U7vb9E5eAs')).json()

index = response4['data'][0]['coordinates'][0]['dates'][0]['value']

print(index)