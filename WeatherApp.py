from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
from dotenv import load_dotenv
from isValidPassword import password_checker


#configure imports for database, environment variables, login management and Flask
app = Flask(__name__)

load_dotenv()

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///userInfo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "Login"


#class for creating a user table in the dataabse
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable = False)
    weather_entries = db.relationship("WeatherHistory", backref="user", lazy=True)

class WeatherHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    city = db.Column(db.String(250))

with app.app_context():
    db.create_all()

#login manager
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


#routing for different pages + API imports
@app.route("/")
def index():
    return render_template("HomePage.html")

@app.route("/SignUp", methods=["GET", "POST"])
def SignUp():

    if request.method == "POST":
        userName = request.form.get("UserName")
        password = request.form.get("Password")

        if Users.query.filter_by(username=userName).first():
            return render_template("SignUp.html", error_message="Username already taken, try another")
        
        password_check = password_checker(password)

        if password_check != "Good password!":
            return render_template("SignUp.html", error_message=password_check)
        hashed_password = generate_password_hash(password)

        newUser = Users(username=userName, password=hashed_password)
        db.session.add(newUser)
        db.session.commit()
        return redirect(url_for("Login"))
    return render_template("SignUp.html")

@app.route("/Login", methods=["GET", "POST"])
def Login():

    if request.method == "POST":
        userName = request.form.get("UserName")
        password = request.form.get("Password")

        user = Users.query.filter_by(username=userName).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("Dashboard"))
        return render_template("Login.html", error_message="Could not find account with the given username/password")

    return render_template("Login.html")

@app.route("/Dashboard", methods=["GET", "POST"])
@login_required
def Dashboard():
    
    empty_msg=None
    API_KEY = os.getenv("API_KEY")

    if request.method == "POST":
        
        action = request.form.get("action")
        
        if action == "add":

            saved_city = request.form.get("city")
            saved_condition = request.form.get("condition")
            saved_temp = request.form.get("temp_celsius")
            saved_temp_feels_like = request.form.get("temp_celsius_feels_like")

            if WeatherHistory.query.filter_by(city=saved_city, user_id=current_user.id).count() >= 1:
                flash(f"Already saved weather for {saved_city}")
                return redirect(url_for("WeatherAppLoggedIn", city_name=saved_city, city_condition=saved_condition, city_temp_celsius=saved_temp, city_temp_feels_like=saved_temp_feels_like, current_user_name = current_user.username))
            
            num_saved_weather = WeatherHistory.query.filter_by(user_id = current_user.id).count()

            if num_saved_weather >= 5:
                flash("Cannot add any more cities, limit reached (5)")
                return redirect(url_for("WeatherAppLoggedIn", city_name=saved_city, city_condition=saved_condition, city_temp_celsius=saved_temp, city_temp_feels_like=saved_temp_feels_like, current_user_name = current_user.username))

            new_entry = WeatherHistory(user_id = current_user.id, city=saved_city)
            db.session.add(new_entry)
            db.session.commit()
            
            return redirect(url_for("WeatherAppLoggedIn", city_name=saved_city, city_condition=saved_condition, city_temp_celsius=saved_temp, city_temp_feels_like=saved_temp_feels_like, current_user_name = current_user.username))

        
        elif action == "delete":
            entry_id = request.form.get("entry_id")
            WeatherHistory.query.filter_by(id=entry_id, user_id=current_user.id).delete()
            db.session.commit()
            return redirect(url_for("Dashboard"))

    weather_history = WeatherHistory.query.filter_by(user_id = current_user.id).all()
    weather_data = []

    for data in weather_history:
        city = data.city
        API_URL_CURR_WEATHER= f"https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
        response = requests.get(API_URL_CURR_WEATHER)

        if response.status_code == 200:
            response_json = response.json()
            weather_data.append({
                "entry_id": data.id,
                "user_id": data.user_id,
                "city": data.city,
                "city_condition": response_json['current']['condition']['text'],
                "city_temp_celsius": response_json['current']['temp_c'],
                "city_temp_celsius_feels_like": response_json['current']['feelslike_c']
            })

        else:
            weather_data.append({
                "entry_id": data.id,
                "user_id": data.user_id,
                "city": data.city,
                "city_condition": "N/A",
                "city_temp_celsius": "N/A",
                "city_temp_celsius_feels_like": "N/A"
            })

    if len(weather_history) == 0:
        empty_msg = "Looks like you don't have any saved weather. Try searching for some with the weather link below:"

    return render_template("Dashboard.html", user=current_user.username, weather_history=weather_data, empty_msg=empty_msg)

@app.route("/Logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("/"))

@app.route("/WeatherApp", methods=["GET", "POST"])
def WeatherApp():

    city_name = None
    city_condition = None
    city_temp_celsius = None
    city_temp_feels_like = None
    error_message = None
    
    API_KEY = os.getenv("API_KEY")

    if request.method == "POST":
        city = request.form.get("city")
        API_URL_CURR_WEATHER = f"https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
        response_crr_weather = requests.get(API_URL_CURR_WEATHER)

        if response_crr_weather.status_code != 200:
            error_message = f"Error: {response_crr_weather.status_code}"
            return render_template("WeatherApp.html", error_message=error_message)

        data_crr_weather = response_crr_weather.json()
        city_name = data_crr_weather['location']['name']
        city_condition = data_crr_weather['current']['condition']['text']
        city_temp_celsius = data_crr_weather['current']['temp_c']
        city_temp_feels_like = data_crr_weather['current']['feelslike_c']

    return render_template("WeatherApp.html", city_name=city_name, city_condition=city_condition, city_temp_celsius=city_temp_celsius, city_temp_feels_like=city_temp_feels_like)

@app.route("/WeatherAppLoggedIn", methods=["GET", "POST"])
@login_required
def WeatherAppLoggedIn():

    city_name = None
    city_condition = None
    city_temp_celsius = None
    city_temp_feels_like = None
    error_message = None
    
    API_KEY = os.getenv("API_KEY")

    if request.method == "POST":
        city = request.form.get("city")
        API_URL_CURR_WEATHER = f"https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
        response_crr_weather = requests.get(API_URL_CURR_WEATHER)

        if response_crr_weather.status_code != 200:
            error_message = f"Error: {response_crr_weather.status_code}"
            return render_template("WeatherAppLoggedIn.html", error_message=error_message) 
        
        data_crr_weather = response_crr_weather.json()
        city_name = data_crr_weather['location']['name']
        city_condition = data_crr_weather['current']['condition']['text']
        city_temp_celsius = data_crr_weather['current']['temp_c']
        city_temp_feels_like = data_crr_weather['current']['feelslike_c']

    else:
        city_name = request.args.get("city_name")
        city_condition = request.args.get("city_condition")
        city_temp_celsius = request.args.get("city_temp_celsius")
        city_temp_feels_like = request.args.get("city_temp_feels_like")

    return render_template("WeatherAppLoggedIn.html", city_name=city_name, city_condition=city_condition, city_temp_celsius=city_temp_celsius, city_temp_feels_like=city_temp_feels_like, current_user_name = current_user.username, error_message=error_message)
        
if __name__ == "__main__":
    app.run()