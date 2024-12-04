import threading
import requests
from tkinter import *
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from api import API_KEY1, API_KEY2

# API keys for OpenWeatherMap and NOAA
OPENWEATHER_API_KEY = API_KEY1
NOAA_API_TOKEN = API_KEY2

class WeatherWranglerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Wrangler App")
        self.root.geometry("800x600")

        # Main Menu
        self.create_main_menu()

    def create_main_menu(self):
        menu_frame = Frame(self.root)
        menu_frame.pack(pady=20)

        Label(menu_frame, text="Welcome to the Weather Wrangler App!", font=("Arial", 16)).pack(pady=10)

        Button(menu_frame, text="1. Find Current Weather", command=self.current_weather).pack(pady=5)
        Button(menu_frame, text="2. Historical Weather Predictions", command=self.weather_probabilities).pack(pady=5)
        Button(menu_frame, text="3. Weather Patterns Graph", command=self.weather_patterns_graph).pack(pady=5)

    # ============= Current Weather (OpenWeatherMap API) ============= #
    def current_weather(self):
        weather_frame = Toplevel(self.root, bg="lightblue")
        weather_frame.title("Current Weather")
        weather_frame.geometry("500x400")

        Label(weather_frame, text="Enter City Name:").pack(pady=10)
        self.city_entry = Entry(weather_frame)
        self.city_entry.pack(pady=5)

        Button(weather_frame, text="Get Weather", command=self.display_weather).pack(pady=10)

    def display_weather(self):
        city = self.city_entry.get()
        weather_data = self.fetch_openweather_data(city)
        if weather_data:
            city_name = weather_data['name']
            temperature = weather_data['main']['temp']
            description = weather_data['weather'][0]['description']
            humidity = weather_data['main']['humidity']
            weather_summary = (
                f"\nWeather Summary:\n"
                f"City: {city_name}\n"
                f"Temperature: {round((temperature * 9 / 5) + 32)}\u00b0F\n"
                f"Description: {description.capitalize()}\n"
                f"Humidity: {humidity}%"
            )
            self.show_weather_summary(weather_summary)
        else:
            print("Error: Unable to fetch weather data. Please check the city name or try again.")

    def fetch_openweather_data(self, city):
        api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def show_weather_summary(self, summary):
        summary_window = Toplevel(self.root)
        summary_window.title("Weather Summary")
        summary_window.geometry("400x300")
        Label(summary_window, text=summary, font=("Arial", 12)).pack(pady=10)

    # ============= Historical Weather Predictions (NOAA API) ============= #
    def weather_probabilities(self):
        prob_frame = Toplevel(self.root, bg="#000080")
        prob_frame.title("Historical Weather Predictions")
        prob_frame.geometry("600x400")

        Label(prob_frame, text="Enter City Name:").pack(pady=5)
        self.region_entry = Entry(prob_frame)
        self.region_entry.pack(pady=5)

        Label(prob_frame, text="Enter Date (MM-DD):").pack(pady=5)
        self.date_entry = Entry(prob_frame)
        self.date_entry.pack(pady=5)

        Button(prob_frame, text="Show Historical Weather Predictions", command=self.start_thread).pack(pady=10)

    def start_thread(self):
        # Start a new thread for fetching NOAA data to avoid blocking the GUI
        threading.Thread(target=self.display_weather_probabilities, daemon=True).start()

    def display_weather_probabilities(self):
        city = self.region_entry.get()
        date = self.date_entry.get()

        # Improved date parsing with error handling
        try:
            if len(date) != 5 or date[2] != '-':
                raise ValueError("Date must be in MM-DD format")
            month, day = map(int, date.split('-'))

            if month < 1 or month > 12 or day < 1 or day > 31:
                raise ValueError("Invalid month or day value.")
        except ValueError as ve:
            print(f"Error: {ve}")
            return

        location = self.lookup_location_id(city)
        if not location:
            print("Error: Unable to find location for the given city. Please check the city name or try again.")
            return

        lat, lon = location
        threading.Thread(target=self.fetch_and_process_historical_data, args=(lat, lon, city, month, day), daemon=True).start()

    def lookup_location_id(self, city):
        weather_data = self.fetch_openweather_data(city)
        if not weather_data:
            return None

        lat = weather_data['coord']['lat']
        lon = weather_data['coord']['lon']

        return lat, lon

    def fetch_and_process_historical_data(self, lat, lon, city, month, day):
        data = self.fetch_noaa_historical_data(lat, lon, month, day)
        if data:
            self.process_historical_data(data, city, month, day)
        else:
            print("No data available or error fetching data.")

    def fetch_noaa_historical_data(self, lat, lon, month, day):
        endpoint = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
        headers = {"token": NOAA_API_TOKEN}

        start_year = 2014
        end_year = 2023
        results = []

        for year in range(start_year, end_year + 1):
            startdate = f"{year}-{month:02d}-{day:02d}"
            enddate = f"{year}-{month:02d}-{day:02d}"

            params = {
                "datasetid": "GHCND",
                "datatypeid": "TMAX,TMIN,PRCP,SNOW",
                "startdate": startdate,
                "enddate": enddate,
                "limit": 1000,
                "units": "metric",
                "latitude": lat,
                "longitude": lon,
            }

            response = requests.get(endpoint, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if "results" in data:
                    results.extend(data["results"])
            else:
                print(f"Error: {response.status_code} - {response.text}")

        return results

    def process_historical_data(self, data, city, month, day):
        total_records = len(data)
        if total_records == 0:
            print("No historical data available for the selected date.")
            return

        avg_temp_max = avg_temp_min = total_precipitation = 0
        count_temp_max = count_temp_min = count_precipitation = 0

        for record in data:
            if record["datatype"] == "TMAX":
                avg_temp_max += record["value"]
                count_temp_max += 1
            elif record["datatype"] == "TMIN":
                avg_temp_min += record["value"]
                count_temp_min += 1
            elif record["datatype"] == "PRCP":
                total_precipitation += record["value"]
                count_precipitation += 1

        if count_temp_max > 0:
            avg_temp_max /= count_temp_max
        if count_temp_min > 0:
            avg_temp_min /= count_temp_min
        if count_precipitation > 0:
            avg_precipitation = total_precipitation / count_precipitation
        else:
            avg_precipitation = 0

        prediction_summary = (
            f"\nHistorical Weather Prediction for {city} on {month:02d}-{day:02d}:\n"
            f"Average Maximum Temperature: {round((avg_temp_max * 9 / 5) + 32)}\u00b0
