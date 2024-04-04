import requests
import json
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

class WeatherForecast:
    def __init__(self):
        self.data = {}
        self.load_data_from_file()
    
    def __setitem__(self, key, value):
        self.data[key] = value
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __iter__(self):
        return iter(self.data)
    
    def items(self):
        return self.data.items()
    
    def load_data_from_file(self):
        try:
            with open("weather_forecast_data.json", "r") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            pass
    
    def save_data_to_file(self):
        with open("weather_forecast_data.json", "w") as file:
            json.dump(self.data, file)
    
    def change_city_to_latitude_and_longitude(self, city):
        geolocator = Nominatim(user_agent="weather_app")
        location = geolocator.geocode(city)
        if location and self.is_valid_location(city, location):
            return location.latitude, location.longitude
        else:
            return None, None
    
    def is_valid_location(self, city, location):
        return True
    
    def check_rain_forecast(self, latitude, longitude, date, city):
        city = city.lower()
        if date in self.data and city in self.data[date]:
            return self.data[date][city], 200

        formatted_date = datetime.strptime(date, '%Y-%m-%d').date()

        if formatted_date == datetime.now().date():
            searched_date = formatted_date + timedelta(days=1)
        else:
            searched_date = formatted_date

        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=rain&daily=rain_sum&timezone=Europe%2FWarsaw&start_date={searched_date}&end_date={searched_date}"
        
        if latitude is None or longitude is None:
            return f"Miasto {city} nie istnieje.", 404

        print(f"URL zapytania do API: {url}")

        response = requests.get(url)
        
        try:
            json_data = response.json()
            daily_forecast = json_data.get('daily', [])
            
            print(f"Odpowiedź JSON: {json_data}")
            
            if response.status_code == 200 and 'daily' in json_data and 'rain_sum' in json_data['daily']:
                total_rain_sum = json_data['daily']['rain_sum'][0]
                if total_rain_sum > 0.05:
                    forecast = "Będzie padać"
                elif total_rain_sum <= 0.05:
                    forecast = "Nie będzie padać"
                else:
                    forecast = "Nie wiem"

                if date not in self.data:
                    self.data[date] = {}

                self.data[date][city] = forecast
                self.save_data_to_file()
                return forecast, response.status_code
            else:
                return "Brak danych o deszczu w prognozie pogody.", response.status_code
        
        except json.JSONDecodeError:
            return "Nie udało się przetworzyć danych pogodowych. Serwer zwrócił nieprawidłową odpowiedź.", response.status_code

weather_forecast = WeatherForecast()
user_date = input("Podaj datę w formacie YYYY-mm-dd (np. 2022-11-03): ").strip()
if not user_date:
    user_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

user_location = input("Podaj miasto: ").strip()

latitude, longitude = weather_forecast.change_city_to_latitude_and_longitude(user_location)

if latitude is not None and longitude is not None:
    forecast, status_code = weather_forecast.check_rain_forecast(latitude, longitude, user_date, user_location)
    print(f"Prognoza pogody dla {user_location} na {user_date}: {forecast}")
    print(f"Status kodu HTTP: {status_code}")
elif latitude is None and longitude is None:
    print(f"Miasto {user_location} nie istnieje.")











