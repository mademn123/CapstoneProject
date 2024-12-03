import requests
from tkinter import *
from tkinter import ttk
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
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
        Button(menu_frame, text="2. Weather Probabilities", command=self.weather_probabilities).pack(pady=5)

    # ============= Current Weather (OpenWeatherMap API) ============= #
    def current_weather(self):
        weather_frame = Toplevel(self.root)
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
                f"Temperature: {round((temperature * 9 / 5) + 32)}°F\n"
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

    # ============= Weather Probabilities (NOAA API) ============= #
    def weather_probabilities(self):
        prob_frame = Toplevel(self.root)
        prob_frame.title("Weather Probabilities")
        prob_frame.geometry("600x400")

        Label(prob_frame, text="Enter City Name:").pack(pady=5)
        self.region_entry = Entry(prob_frame)
        self.region_entry.pack(pady=5)

        Label(prob_frame, text="Enter Weather Pattern (e.g., Snow, Tornado):").pack(pady=5)
        self.pattern_entry = Entry(prob_frame)
        self.pattern_entry.pack(pady=5)

        Label(prob_frame, text="Enter Date (YYYY-MM-DD):").pack(pady=5)
        self.date_entry = Entry(prob_frame)
        self.date_entry.pack(pady=5)

        Button(prob_frame, text="Show Weather Probabilities", command=self.display_weather_probabilities).pack(pady=10)

    def lookup_location_id(self, city):
        # Use OpenWeatherMap to get latitude and longitude of the city
        weather_data = self.fetch_openweather_data(city)
        if not weather_data:
            return None

        lat = weather_data['coord']['lat']
        lon = weather_data['coord']['lon']

        # Format the latitude and longitude for NOAA usage
        return lat, lon

    def fetch_noaa_data(self, lat, lon, pattern, date):
        # NOAA API endpoint
        endpoint = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
        headers = {"token": NOAA_API_TOKEN}

        # Map pattern to a NOAA datatypeid
        datatype_mapping = {
            "snow": "SNOW",
            "tornado": "WT04",
            "temperature": "TMAX",  # Example of temperature max (could add more mappings)
            "rain": "PRCP",
        }

        datatypeid = datatype_mapping.get(pattern.lower())
        if not datatypeid:
            print("Error: Unsupported weather pattern. Please use 'snow', 'tornado', 'temperature', or 'rain'.")
            return None

        params = {
            "datasetid": "GHCND",  # Global Historical Climatology Network Daily
            "datatypeid": datatypeid,  # Weather pattern (e.g., SNOW, WT04 for tornadoes)
            "startdate": date,
            "enddate": date,
            "limit": 1000,  # Maximum results
            "units": "metric",
            "latitude": lat,
            "longitude": lon,
        }

        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def display_weather_probabilities(self):
        city = self.region_entry.get()
        pattern = self.pattern_entry.get()
        date = self.date_entry.get()

        # Lookup latitude and longitude for the given city
        location = self.lookup_location_id(city)
        if not location:
            print("Error: Unable to find location for the given city. Please check the city name or try again.")
            return

        lat, lon = location

        # Fetch NOAA data
        data = self.fetch_noaa_data(lat, lon, pattern, date)
        if data and "results" in data:
            # Process the data as needed and display it
            self.show_probability_map(data, city, pattern, date)
        else:
            print("No data available or error fetching data.")

    def show_probability_map(self, data, region, pattern, date):
        # Simulate NOAA data for map visualization
        locations = [
            {"lat": 40.7128, "lon": -74.0060, "value": 50},  # Example: New York
            {"lat": 34.0522, "lon": -118.2437, "value": 70},  # Example: Los Angeles
            {"lat": 41.8781, "lon": -87.6298, "value": 30},  # Example: Chicago
        ]

        map_window = Toplevel(self.root)
        map_window.title("Weather Probability Map")
        map_window.geometry("800x600")

        fig = plt.figure(figsize=(10, 8))
        m = Basemap(projection="mill", llcrnrlat=20, urcrnrlat=50, llcrnrlon=-130, urcrnrlon=-60)

        m.drawcoastlines()
        m.drawcountries()
        m.drawstates()

        for loc in locations:
            x, y = m(loc["lon"], loc["lat"])
            m.scatter(x, y, s=loc["value"], color="red", alpha=0.7)

        plt.title(f"Probability of {pattern} on {date} in {region}")
        canvas = FigureCanvasTkAgg(fig, master=map_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

        Button(map_window, text="Close", command=map_window.destroy).pack(pady=10)


# Run App
root = Tk()
app = WeatherWranglerApp(root)
root.mainloop()
