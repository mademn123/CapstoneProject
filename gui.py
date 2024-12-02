import requests
from tkinter import *
from tkinter import ttk
from api import API_KEY1, API_KEY2


api_key1 = API_KEY1
api_key2 = API_KEY2
# Main App Class
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

    def current_weather(self):
        # Weather input frame
        weather_frame = Toplevel(self.root)
        weather_frame.title("Current Weather")
        weather_frame.geometry("500x400")

        # Asking user for location (city)
        Label(weather_frame, text="Enter City Name:").pack(pady=10)
        self.city_entry = Entry(weather_frame)
        self.city_entry.pack(pady=5)

        Button(weather_frame, text="Get Weather", command=self.display_weather).pack(pady=10)

    def display_weather(self):
        city = self.city_entry.get()

        # Fetch the weather data for the city
        weather_data = self.fetch_weather_data_by_city(city)

        # Display the fetched weather data
        if weather_data:
            # Extract relevant weather data
            city_name = weather_data['name']
            temperature = weather_data['main']['temp']
            description = weather_data['weather'][0]['description']
            humidity = weather_data['main']['humidity']

            # Display weather summary
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

    def fetch_weather_data_by_city(self, city):
        # OpenWeather API URL (replace YOUR_API_KEY with a valid API key)
        api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key1}&units=metric"
        response = requests.get(api_url)

        # Print response for debugging
        print(response.status_code)
        print(response.text)

        # Check if the response is successful
        if response.status_code == 200:
            return response.json()  # Parse and return the JSON response
        else:
            print("Error: Unable to fetch weather data.")
            return None

    def show_weather_summary(self, summary):
        # Create a new window to display the weather summary
        summary_window = Toplevel(self.root)
        summary_window.title("Weather Summary")
        summary_window.geometry("400x300")
        Label(summary_window, text=summary, font=("Arial", 12)).pack(pady=10)

    def weather_probabilities(self):
        prob_frame = Toplevel(self.root)
        prob_frame.title("Weather Probabilities")

        Label(prob_frame, text="Weather Probabilities", font=("Arial", 14)).pack(pady=10)
        Button(prob_frame, text="Region", command=self.select_region).pack(pady=5)
        Button(prob_frame, text="Weather Pattern", command=self.select_pattern).pack(pady=5)
        Button(prob_frame, text="Date", command=self.select_date).pack(pady=5)

    def select_region(self):
        print("Region selection UI")

    def select_pattern(self):
        print("Pattern selection UI")

    def select_date(self):
        print("Date selection UI")


# Run App
root = Tk()
app = WeatherWranglerApp(root)
root.mainloop()