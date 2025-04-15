import streamlit as st
import folium
from streamlit_folium import folium_static
import requests
import time

st.title("WindBorne Balloon Tracker")

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_balloon_data():
    balloons = []
    for hour in range(24):
        try:
            url = f"https://a.windbornesystems.com/treasure/{hour:02d}.json"
            response = requests.get(url, timeout=5)
            data = response.json()
            for balloon in data.get("balloons", []):
                try:
                    balloons.append({
                        "id": balloon["id"],
                        "lat": float(balloon["latitude"]),
                        "lon": float(balloon["longitude"]),
                        "alt": float(balloon["altitude"]),
                        "timestamp": balloon["timestamp"]
                    })
                except (KeyError, ValueError):
                    pass
        except requests.RequestException:
            pass
    return balloons

def fetch_weather(lat, lon):
    api_key = st.secrets.get("OPENWEATHER_API_KEY", "your_api_key_123")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        return {
            "temp": data["main"]["temp"],
            "weather": data["weather"][0]["description"]
        }
    except requests.RequestException:
        return None

# Fetch data
balloon_data = fetch_balloon_data()
if not balloon_data:
    st.error("No balloon data available.")
    st.stop()

# Create map
m = folium.Map(location=[0, 0], zoom_start=2)
for balloon in balloon_data:
    weather = fetch_weather(balloon["lat"], balloon["lon"])
    popup = f"""
    <b>Balloon {balloon['id']}</b><br>
    Lat: {balloon['lat']:.2f}, Lon: {balloon['lon']:.2f}<br>
    Altitude: {balloon['alt']} m<br>
    Time: {balloon['timestamp']}<br>
    {f"Weather: {weather['temp']}°C, {weather['weather']}" if weather else "No weather data"}
    """
    folium.Marker(
        [balloon["lat"], balloon["lon"]],
        popup=popup
    ).add_to(m)

# Display map
folium_static(m)

# Auto-refresh
st.write("Updates hourly. Last updated:", time.ctime())
