from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
from dotenv import load_dotenv

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///userInfo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "supersecretkey"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable = False)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route("/")
def index():
    return render_template("SignUp.html")

@app.route("/WeatherApp", methods=["GET", "POST"])
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
    
if __name__ == "__main__":
    app.run(debug=True)