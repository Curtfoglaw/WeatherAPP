import requests
import os
from dotenv import load_dotenv
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def WeatherApp():

    city_name = None
    city_condition = None
    city_temp_celsius = None
    city_temp_feels_like = None
    error_message = None
    load_dotenv()
    API_KEY = os.getenv("API_KEY")

    if request.method == "POST":
        city = request.form.get("city")
        API_URL_CURR_WEATHER = f"https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
        response_crr_weather = requests.get(API_URL_CURR_WEATHER)

        if response_crr_weather.status_code != 200:
            error_message = "Please enter a valid city name"
            return render_template("WeatherApp.html", error_message=error_message)

        data_crr_weather = response_crr_weather.json()
        city_name = data_crr_weather['location']['name']
        city_condition = data_crr_weather['current']['condition']['text']
        city_temp_celsius = data_crr_weather['current']['temp_c']
        city_temp_feels_like = data_crr_weather['current']['feelslike_c']

    return render_template("WeatherApp.html", city_name=city_name, city_condition=city_condition, city_temp_celsius=city_temp_celsius, city_temp_feels_like=city_temp_feels_like)
    
