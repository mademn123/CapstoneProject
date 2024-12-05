import threading
from tkinter.ttk import Combobox
import numpy as np
import requests
from tkinter import *
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from api import API_KEY1, API_KEY2
from PIL import Image, ImageTk
from tkinter import Toplevel, Label, Canvas, Frame, Scrollbar, Button

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
        menu_frame = Frame(self.root, bg="#87CEEB", bd=5, relief="solid")
        menu_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Create Canvas
        self.canvas = Canvas(menu_frame, width=800, height=200, bg="#87CEEB", bd=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Load and add the cloud image with Pillow
        cloud_image = Image.open(r"C:\Users\mvvsg\PycharmProjects\CapstoneProject\newcloud.png")
        self.cloud_image = ImageTk.PhotoImage(cloud_image)
        self.cloud = self.canvas.create_image(-100, 50, image=self.cloud_image, anchor="nw")

        # Animate the cloud
        def animate_cloud():
            current_x = self.canvas.coords(self.cloud)[0]
            if current_x < 800:
                new_x = current_x + 2
                self.canvas.coords(self.cloud, new_x, 50)
            else:
                self.canvas.coords(self.cloud, -100, 50)
            self.canvas.after(20, animate_cloud)

        animate_cloud()

        # Adjust the vertical padding for the label to move everything up
        Label(menu_frame, text="Welcome to the Weather Wrangler App!", font=("Arial", 16, 'bold'),
              bg="#87CEEB").pack(pady=5)

        # Create buttons using the new styled_button function
        self.styled_button(menu_frame, "Find Current Weather", self.current_weather)
        self.styled_button(menu_frame, "Historical Predictions", self.weather_probabilities)
        self.styled_button(menu_frame, "Weather Visualization", self.weather_pattern_visualization)

    # Button styling function
    def styled_button(self, parent, text, command):
        button = Button(parent, text=text, command=command, font=("Arial", 12), width=30, height=2,
                        bg="#4CAF50",  # Green color for consistency
                        fg="white",    # White text for good contrast
                        relief="raised", bd=3,
                        activebackground="#45A049",  # Slightly darker green when pressed
                        activeforeground="white"  # White text color when the button is pressed
                        )
        button.pack(pady=5)

    # ============= Current Weather (OpenWeatherMap API) ============= #
    def current_weather(self):
        weather_frame = Toplevel(self.root, bg="#ADD8E6")  # Light blue background
        weather_frame.title("Current Weather")
        weather_frame.geometry("500x400")

        Label(weather_frame, text="Enter City Name:", font=("Arial", 12, "bold"), bg="#ADD8E6").pack(pady=10)
        self.city_entry = Entry(weather_frame, font=("Arial", 12))
        self.city_entry.pack(pady=5)

        self.styled_button(weather_frame, "Get Weather", self.display_weather)

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
        # Create the new window
        summary_window = Toplevel(self.root)
        summary_window.title("Weather Summary")
        summary_window.geometry("500x400")

        # Set the window background
        summary_window.configure(bg="#0047AB")  # Royal blue background

        # Add a title label, centered
        title_label = Label(
            summary_window,
            text="Weather Summary",
            font=("Arial", 16, "bold"),
            bg="#0047AB",
            fg="#FFD700"
        )
        title_label.pack(pady=20)

        # Create a frame to contain the summary and button, ensuring it's centered
        content_frame = Frame(summary_window, bg="#0047AB")
        content_frame.pack(fill="both", expand=True)

        # Add the summary text, centered
        summary_label = Label(
            content_frame,
            text=summary,
            font=("Arial", 12),
            bg="#0047AB",
            fg="#FFD700",
            wraplength=450,
            justify="center"
        )
        summary_label.pack(pady=10)

        # Add the close button, centered below the summary data
        self.styled_button(content_frame, "Close", summary_window.destroy)

    # ============= Historical Weather Predictions (NOAA API) ============= #
    def weather_probabilities(self):
        prob_frame = Toplevel(self.root,  bg="#ADD8E6")  # Light blue background
        prob_frame.title("Historical Weather Predictions")
        prob_frame.geometry("600x400")

        Label(prob_frame, text="Enter City Name:", font=("Arial", 12, "bold"), bg="#ADD8E6").pack(pady=5)
        self.region_entry = Entry(prob_frame, font=("Arial", 12))
        self.region_entry.pack(pady=5)

        Label(prob_frame, text="Enter Date (MM-DD):", font=("Arial", 12, "bold"), bg="#ADD8E6").pack(pady=5)
        self.date_entry = Entry(prob_frame, font=("Arial", 12))
        self.date_entry.pack(pady=5)

        self.styled_button(prob_frame, "Show Historical Weather Predictions", self.start_thread)

    # ============= Weather Pattern Visualization ============= #
    def weather_pattern_visualization(self):
        pattern_frame = Toplevel(self.root, bg="#ADD8E6")  # Light blue background
        pattern_frame.title("Weather Pattern Visualization")
        pattern_frame.geometry("600x500")

        # Dropdown for weather pattern
        Label(pattern_frame, text="Select Weather Pattern:", font=("Arial", 12, "bold"), bg="#ADD8E6").pack(pady=10)

        # Only store the user-friendly names in the combobox
        self.pattern_combobox = Combobox(pattern_frame, values=[
            "Max Temperature", "Min Temperature", "Precipitation", "Snowfall", "Average Temperature"
        ], font=("Arial", 12))
        self.pattern_combobox.pack(pady=5)

        # Date and City entries
        Label(pattern_frame, text="Enter Date (MM-DD):", font=("Arial", 12, "bold"), bg="#ADD8E6").pack(pady=10)
        self.date_entry_pattern = Entry(pattern_frame, font=("Arial", 12))
        self.date_entry_pattern.pack(pady=5)

        Label(pattern_frame, text="Enter City:", font=("Arial", 12, "bold"), bg="#ADD8E6").pack(pady=10)
        self.city_entry_pattern = Entry(pattern_frame, font=("Arial", 12))
        self.city_entry_pattern.pack(pady=5)

        self.styled_button(pattern_frame, "Show Weather Pattern", self.start_pattern_thread)

    def start_thread(self):
        # Start a new thread for fetching NOAA data to avoid blocking the GUI
        threading.Thread(target=self.display_weather_probabilities, daemon=True).start()

    def start_pattern_thread(self):
        # Start a new thread for fetching NOAA data to avoid blocking the GUI
        threading.Thread(target=self.fetch_weather_pattern_data, daemon=True).start()

    def fetch_weather_pattern_data(self):
        # Implementation here for fetching and displaying weather patterns
        pass

    # Rest of your methods here...

# Run App
try:
    root = Tk()
    app = WeatherWranglerApp(root)
    root.mainloop()
except Exception as e:
    print(f"An error occurred: {e}")
