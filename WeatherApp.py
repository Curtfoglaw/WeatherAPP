import requests

def WeatherApp():
    
    API_KEY = "10426a25d521462cbe8125307261106"

    print("---WELCOME TO THE WEATHER APP---")
    
    city = input("What city would you like to view the weather for today?: ").capitalize()

    API_URL_CURR_WEATHER = f"https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
    response_crr_weather = requests.get(API_URL_CURR_WEATHER)

    if response_crr_weather.status_code != 200:
        return "Request failed"

    data_crr_weather = response_crr_weather.json()
    city_name = data_crr_weather['location']['name']
    city_condition = data_crr_weather['current']['condition']['text']
    city_temp_celsius = data_crr_weather['current']['temp_c']
    city_temp_feels_like = data_crr_weather['current']['feelslike_c']


    """print(data_crr_weather)"""
    print(f"City: {city_name}\n")
    print(f"Condition: {city_condition}\n")
    print(f"Temperature (C): {city_temp_celsius}\n")
    print(f"Temperature feels like (C): {city_temp_feels_like}\n")

WeatherApp()