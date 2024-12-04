import threading
import requests
from tkinter import *
from tkinter import ttk
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from api import API_KEY1, API_KEY2
from PIL import Image, ImageTk


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
        menu_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Create Canvas
        self.canvas = Canvas(menu_frame, width=800, height=300, bg="#87CEEB", bd=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Load and add the cloud image
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

        Label(menu_frame, text="Welcome to the Weather Wrangler App!", font=("Arial", 16, 'bold'),
              bg="#87CEEB").pack(pady=10)

        def create_button(text, command):
            button = Button(menu_frame, text=text, command=command, font=("Arial", 12), width=30, height=2,
                            bg="#4CAF50", fg="white", relief="raised", bd=3, activebackground="#45a049",
                            activeforeground="white")
            button.pack(pady=10)

        def current_weather():
            print("Current weather selected")

        def weather_probabilities():
            print("Historical weather predictions selected")

        create_button("1. Find Current Weather", self.current_weather)
        create_button("2. Historical Weather Predictions", self.weather_probabilities)
        create_button("3. Weather Pattern Visualization", self.weather_pattern_visualization)

    '''
    def create_main_menu(self):
        menu_frame = Frame(self.root)
        menu_frame.pack(pady=20)

        Label(menu_frame, text="Welcome to the Weather Wrangler App!", font=("Arial", 16)).pack(pady=10)

        Button(menu_frame, text="1. Find Current Weather", command=self.current_weather).pack(pady=5)
        Button(menu_frame, text="2. Historical Weather Predictions", command=self.weather_probabilities).pack(pady=5)
        Button(menu_frame, text="3. Weather Pattern Visualization", command=self.weather_pattern_visualization).pack(pady=5)
        '''

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

    # ============= Historical Weather Predictions (NOAA API) ============= #
    def weather_probabilities(self):
        prob_frame = Toplevel(self.root,  bg="#000080")
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

        # Lookup latitude and longitude for the given city
        location = self.lookup_location_id(city)
        if not location:
            print("Error: Unable to find location for the given city. Please check the city name or try again.")
            return

        lat, lon = location

        # Start a thread to fetch NOAA historical data
        threading.Thread(target=self.fetch_and_process_historical_data, args=(lat, lon, city, month, day),
                         daemon=True).start()

    def lookup_location_id(self, city):
        # Use OpenWeatherMap to get latitude and longitude of the city
        weather_data = self.fetch_openweather_data(city)
        if not weather_data:
            return None

        lat = weather_data['coord']['lat']
        lon = weather_data['coord']['lon']

        return lat, lon

    def fetch_and_process_historical_data(self, lat, lon, city, month, day):
        # Fetch NOAA historical data
        data = self.fetch_noaa_historical_data(lat, lon, month, day)
        if data:
            self.process_historical_data(data, city, month, day)
        else:
            print("No data available or error fetching data.")

    def fetch_noaa_historical_data(self, lat, lon, month, day):
        # NOAA API endpoint
        endpoint = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
        headers = {"token": NOAA_API_TOKEN}

        # Retrieve data for multiple years (e.g., last 10 years)
        start_year = 2014
        end_year = 2023
        results = []

        for year in range(start_year, end_year + 1):
            startdate = f"{year}-{month:02d}-{day:02d}"
            enddate = f"{year}-{month:02d}-{day:02d}"

            params = {
                "datasetid": "GHCND",  # Global Historical Climatology Network Daily
                "datatypeid": "TMAX,TMIN,PRCP,SNOW",  # Collect relevant data types
                "startdate": startdate,
                "enddate": enddate,
                "limit": 1000,  # Maximum results
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
        # Initialize counters and sums for each data type
        total_records = len(data)
        if total_records == 0:
            print("No historical data available for the selected date.")
            return

        avg_temp_max = avg_temp_min = total_precipitation = 0
        count_temp_max = count_temp_min = count_precipitation = count_snow = 0
        snow_days = 0

        # Loop through the data to aggregate information
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
            elif record["datatype"] == "SNOW":
                count_snow += 1
                if record["value"] > 0:
                    snow_days += 1

        # Safely calculate averages if there is data available
        if count_temp_max > 0:
            avg_temp_max /= count_temp_max
        if count_temp_min > 0:
            avg_temp_min /= count_temp_min
        if count_precipitation > 0:
            avg_precipitation = total_precipitation / count_precipitation
        else:
            avg_precipitation = 0

        snow_probability = (snow_days / count_snow) * 100 if count_snow > 0 else 0

        # Create prediction summary
        prediction_summary = (
            f"\nHistorical Weather Prediction for {city} on {month:02d}-{day:02d}:\n"
            f"Average Maximum Temperature: {round((avg_temp_max * 9 / 5) + 32)}°F\n"
            f"Average Minimum Temperature: {round((avg_temp_min * 9 / 5) + 32)}°F\n"
            f"Average Precipitation: {avg_precipitation:.2f} mm\n"
            f"Probability of Snow: {snow_probability:.2f}%"
        )
        # Use the main thread to show the weather summary in the GUI
        self.root.after(0, lambda: self.show_weather_summary(prediction_summary))

    def show_weather_summary(self, summary):
        summary_window = Toplevel(self.root)
        summary_window.title("Weather Summary")
        summary_window.geometry("400x300")
        Label(summary_window, text=summary, font=("Arial", 12)).pack(pady=10)

    # ============= Weather Pattern Visualization ============= #
    def weather_pattern_visualization(self):
        pattern_frame = Toplevel(self.root)
        pattern_frame.title("Weather Pattern Visualization")
        pattern_frame.geometry("600x500")

        Label(pattern_frame, text="Enter Weather Pattern:").pack(pady=10)
        self.pattern_entry = Entry(pattern_frame)
        self.pattern_entry.pack(pady=5)

        Label(pattern_frame, text="Enter Date (MM-DD):").pack(pady=10)
        self.date_entry_pattern = Entry(pattern_frame)
        self.date_entry_pattern.pack(pady=5)

        Label(pattern_frame, text="Enter City:").pack(pady=10)
        self.city_entry_pattern = Entry(pattern_frame)
        self.city_entry_pattern.pack(pady=5)

        Button(pattern_frame, text="Show Weather Pattern", command=self.start_pattern_thread).pack(pady=20)

    def start_pattern_thread(self):
        # Start a new thread for fetching NOAA data to avoid blocking the GUI
        threading.Thread(target=self.fetch_weather_pattern_data, daemon=True).start()

    def fetch_weather_pattern_data(self):
        pattern = self.pattern_entry.get().strip().upper()
        date = self.date_entry_pattern.get().strip()
        city = self.city_entry_pattern.get().strip()

        # Validate the weather pattern type
        valid_patterns = ["TMAX", "TMIN", "PRCP", "SNOW"]
        if pattern not in valid_patterns:
            messagebox.showerror("Invalid Pattern", f"Please enter one of the following patterns: {', '.join(valid_patterns)}")
            return

        # Input validation for date
        try:
            if len(date) != 5 or date[2] != '-':
                raise ValueError("Date must be in MM-DD format")
            month, day = map(int, date.split('-'))

            if month < 1 or month > 12 or day < 1 or day > 31:
                raise ValueError("Invalid month or day value.")
        except ValueError as ve:
            messagebox.showerror("Invalid Date", f"Error: {ve}")
            return

        # Fetch data from NOAA API for this city and date
        location = self.lookup_location_id(city)
        if location:
            lat, lon = location
            data = self.fetch_noaa_historical_data(lat, lon, month, day)
            if data:
                self.root.after(0, lambda: self.plot_weather_pattern(data, pattern))
            else:
                messagebox.showerror("Data Error", "No data available for the selected date and location.")
        else:
            messagebox.showerror("Location Error", "Unable to find city location. Please check the city name.")

    def plot_weather_pattern(self, data, pattern):
        # Check if data is available
        if not data:
            messagebox.showerror("Data Error", "No data available for the selected pattern.")
            return

        # Filter data for the selected pattern
        values = [record["value"] for record in data if record["datatype"] == pattern]
        dates = [record["date"] for record in data if record["datatype"] == pattern]

        # Ensure there is enough data to plot
        if not values or not dates:
            messagebox.showerror("Data Error", f"No records found for pattern '{pattern}'.")
            return

        # Convert dates to a readable format
        readable_dates = [date.split("T")[0] for date in dates]

        # Plotting
        try:
            fig, ax = plt.subplots()
            ax.plot(readable_dates, values, marker="o", linestyle="-")
            ax.set_title(f"{pattern.capitalize()} Pattern for Selected Date")
            ax.set_xlabel("Date")
            ax.set_ylabel("Value")
            ax.grid(True)

            # Display plot in the GUI
            plot_window = Toplevel(self.root)
            plot_window.title("Weather Pattern Plot")
            plot_window.geometry("800x600")

            canvas = FigureCanvasTkAgg(fig, master=plot_window)
            canvas.get_tk_widget().pack()
            canvas.draw()
        except Exception as e:
            print(f"Error while plotting data: {e}")
            messagebox.showerror("Plotting Error", f"An error occurred while plotting: {e}")

# Run App
try:
    root = Tk()
    app = WeatherWranglerApp(root)
    root.mainloop()
except Exception as e:
    print(f"An error occurred: {e}")
