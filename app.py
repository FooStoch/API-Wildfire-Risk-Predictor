import streamlit as st
import streamlit.components.v1 as components  # Explicit import
import tensorflow as tf
import keras
import requests
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
import joblib

# Inject JavaScript to handle localStorage errors
components.html("""
<script>
// Override localStorage to prevent null errors in WebView
if (!window.localStorage) {
    window.localStorage = {
        getItem: function(key) { return null; },
        setItem: function(key, value) {},
        removeItem: function(key) {},
        clear: function() {}
    };
} else {
    // Wrap getItem in try-catch for safety
    var originalGetItem = window.localStorage.getItem;
    window.localStorage.getItem = function(key) {
        try {
            return originalGetItem.call(window.localStorage, key);
        } catch (e) {
            console.warn("localStorage.getItem failed:", e);
            return null;
        }
    };
}
</script>
""", height=0)

# Load the trained model and scaler
model = load_model('wildfire_risk_model.keras', compile=False)
scaler = joblib.load('scaler.pkl')

# Function to get weather and elevation data
def get_weather_data(lat, lon):
    try:
        # National Weather Service API
        response = requests.get(f'https://api.weather.gov/points/{lat},{lon}').json()
        gridX = response["properties"]["gridX"]
        gridY = response["properties"]["gridY"]
        cwa = response["properties"]["cwa"]
        response_hourly = requests.get(f'https://api.weather.gov/gridpoints/{cwa}/{gridX},{gridY}/forecast/hourly').json()

        elevation = response_hourly["properties"]["elevation"]["value"]  # m
        temperature = response_hourly["properties"]["periods"][0]["temperature"]  # deg F
        precipitationProbability = response_hourly["properties"]["periods"][0]["probabilityOfPrecipitation"]["value"]  # %
        dewpoint = response_hourly["properties"]["periods"][0]["dewpoint"]["value"]  # deg C
        humidity = response_hourly["properties"]["periods"][0]["relativeHumidity"]["value"]  # %
        windSpeed = response_hourly["properties"]["periods"][0]["windSpeed"].split()[0]  # mph

        return {
            "elevation": elevation,
            "temperature": temperature,
            "precipitationProbability": precipitationProbability,
            "dewpoint": dewpoint,
            "humidity": humidity,
            "windSpeed": windSpeed,
        }
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return None

# Streamlit app layout
st.title("Wildfire Risk Prediction")
st.write("Enter latitude and longitude to predict the Forest Fire Index.")
st.write(f"Streamlit version: {st.__version__}")  # Temporary version check

# Input fields
lat = st.number_input("Enter Latitude:", format="%.6f")
lon = st.number_input("Enter Longitude:", format="%.6f")

if st.button("Predict"):
    # Get weather data
    weather_data = get_weather_data(lat, lon)

    if weather_data:
        st.write("Weather Data Retrieved:")
        st.json(weather_data)

        # Prepare inputs for prediction
        inputs = np.array([[weather_data["dewpoint"], weather_data["elevation"],
                            weather_data["humidity"], lat, lon,
                            weather_data["precipitationProbability"],
                            weather_data["temperature"], weather_data["windSpeed"]]])

        # Scale inputs
        inputs = scaler.transform(inputs)

        # Make prediction
        prediction = model.predict(inputs)
        predicted_index = prediction[0][0]

        # Display prediction
        st.success(f"Predicted Wildfire Risk Index: {predicted_index:.4f}")
