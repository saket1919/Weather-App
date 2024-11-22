import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
from dotenv import load_dotenv
import os

# Function to fetch weather data
def get_weather_data(city, api_key):
    BASE_URL = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        if data["cod"] == "200":
            current_weather = {
                "city": data["city"]["name"],
                "temperature": data["list"][0]["main"]["temp"],
                "description": data["list"][0]["weather"][0]["description"].capitalize(),
                "humidity": data["list"][0]["main"]["humidity"],
                "wind_speed": data["list"][0]["wind"]["speed"],
                "pressure": data["list"][0]["main"]["pressure"],
                "icon": f"http://openweathermap.org/img/wn/{data['list'][0]['weather'][0]['icon']}@2x.png",
                "latitude": data["city"]["coord"]["lat"],
                "longitude": data["city"]["coord"]["lon"],
                "sunrise": datetime.fromtimestamp(data["city"]["sunrise"]).strftime('%H:%M:%S'),
                "sunset": datetime.fromtimestamp(data["city"]["sunset"]).strftime('%H:%M:%S'),
            }
            forecast = [
                {
                    "date": (datetime.now() + timedelta(days=i // 8)).strftime('%Y-%m-%d'),
                    "temp": data["list"][i]["main"]["temp"],
                    "description": data["list"][i]["weather"][0]["description"].capitalize(),
                    "icon": f"http://openweathermap.org/img/wn/{data['list'][i]['weather'][0]['icon']}@2x.png"
                }
                for i in range(0, 40, 8)
            ]
            return current_weather, forecast
        else:
            st.error(f"City not found: {data.get('message', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
    return None, None

# Streamlit page configuration
st.set_page_config(
    page_title="SriniWeather Check",
    page_icon="🌦️",
    layout="wide",
)

# Custom CSS for Responsiveness and Design
st.markdown("""
    <style>
    body {
        margin: 0;
        padding: 0;
    }
    .tile {
        background-color: #005BEA;
        color: white;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        padding: 20px;
        margin: 15px;
        text-align: center;
        transition: transform 0.2s;
    }
    .tile:hover {
        transform: scale(1.05);
    }
    .header {
        text-align: center;
        padding: 20px;
        background-color: #005BEA;
        color: white;
        border-radius: 10px;
    }
    .card {
        background-color: white;
        color: black;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        padding: 15px;
        margin: 10px auto;
        max-width: 95%; /* Dynamic width adjustment for responsiveness */
        text-align: center;
    }
    @media (max-width: 768px) {
        .tile {
            margin: 10px;
            padding: 15px;
        }
        .card {
            padding: 10px;
            font-size: 14px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
    <div class="header">
        <h1>🌦️ SriniWeather Check</h1>
        <p>Interactive weather insights with dynamic, mobile-friendly design.</p>
    </div>
""", unsafe_allow_html=True)

# Input Section
city = st.text_input("Enter City Name", placeholder="E.g., London, Tokyo")
submit = st.button("Get Weather")

load_dotenv()
API_KEY = os.getenv("API_KEY")

current_weather, forecast = None, None

if submit:
    with st.spinner("Fetching weather data..."):
        if city.strip():
            current_weather, forecast = get_weather_data(city, API_KEY)
        else:
            st.warning("Please enter a valid city name.")

# Display Tiles and Card
if current_weather:
    st.markdown("<h3 style='text-align: center;'>Weather Overview</h3>", unsafe_allow_html=True)

    # Short Description Card (Dynamic)
    st.markdown(f"""
    <div class="card">
        <h2>🌍 {current_weather['city']}</h2>
        <p>Today's weather is <b>{current_weather['description']}</b> with a temperature of <b>{current_weather['temperature']}°C</b>.</p>
        <p>Wind speed is <b>{current_weather['wind_speed']} m/s</b>, and humidity is <b>{current_weather['humidity']}%</b>.</p>
    </div>
    """, unsafe_allow_html=True)

    # Tile Grid Layout
    cols = st.columns(3)

    # Current Weather Tile
    with cols[0]:
        st.markdown(f"""
        <div class="tile">
            <h2>{current_weather['city']}</h2>
            <img src="{current_weather['icon']}" alt="{current_weather['description']}">
            <p><b>{current_weather['description']}</b></p>
            <p><b>Temperature:</b> {current_weather['temperature']}°C</p>
        </div>
        """, unsafe_allow_html=True)

    # Sunrise & Sunset Tile
    with cols[1]:
        st.markdown(f"""
        <div class="tile">
            <h2>Sunrise & Sunset</h2>
            <p><b>Sunrise:</b> {current_weather['sunrise']} 🌅</p>
            <p><b>Sunset:</b> {current_weather['sunset']} 🌇</p>
        </div>
        """, unsafe_allow_html=True)

    # Wind & Humidity Tile
    with cols[2]:
        st.markdown(f"""
        <div class="tile">
            <h2>Wind & Humidity</h2>
            <p><b>Wind Speed:</b> {current_weather['wind_speed']} m/s</p>
            <p><b>Humidity:</b> {current_weather['humidity']}%</p>
        </div>
        """, unsafe_allow_html=True)

    # Forecast and Radar Section
    st.markdown("<h3 style='text-align: center;'>10-Day Forecast and Radar</h3>", unsafe_allow_html=True)
    cols2 = st.columns([2, 1])  # Forecast on the left, radar on the right

    # 10-Day Forecast Visualization
    with cols2[0]:
        forecast_df = pd.DataFrame(forecast)
        fig_forecast = px.line(
            forecast_df,
            x="date",
            y="temp",
            text="description",
            title="10-Day Temperature Forecast",
            labels={"temp": "Temperature (°C)", "date": "Date"}
        )
        st.plotly_chart(fig_forecast, use_container_width=True)

    # Weather Radar Tile
    with cols2[1]:
        st.markdown("<div class='tile'><h2>Weather Radar</h2></div>", unsafe_allow_html=True)
        radar_map = folium.Map(location=[current_weather["latitude"], current_weather["longitude"]], zoom_start=8)
        folium.TileLayer(
            tiles=f"https://tile.openweathermap.org/map/temp_new/{{z}}/{{x}}/{{y}}.png?appid={API_KEY}",
            attr="OpenWeatherMap",
            name="Temperature",
        ).add_to(radar_map)
        folium_static(radar_map)
