from flask import Blueprint, render_template, redirect, request
from .functions import open_weather_api, open_weather_clean_data, get_solar_production, get_monthly_production, get_plot, get_modules_inverters


# static_folder / template_folder => optional
views = Blueprint("views", __name__, static_folder="static", template_folder="templates")

# set-up route & function
@views.route("/", methods=["GET","POST"])
def home():

    modules, inverters = get_modules_inverters()

    # when "Check" clicked
    if request.method == "POST":

        # ensure each input is typed/selected
        if not request.form["city"]:
<<<<<<< HEAD
            message = "Missing input #1."
            return render_template("index.html", message=message, modules=modules, inverters=inverters)
        if not request.form.get("modules"):
            message = "Missing input #2."
            return render_template("index.html", message=message, modules=modules, inverters=inverters)
        if not request.form.get("inverters"):
            message = "Missing input #3."
            return render_template("index.html", message=message, modules=modules, inverters=inverters)
        if not request.form["tilt"]:
            message = "Missing input #4."
            return render_template("index.html", message=message, modules=modules, inverters=inverters)
        if not request.form["azimuth"]:
            message = "Missing input #5."
            return render_template("index.html", message=message, modules=modules, inverters=inverters)
        if not request.form["multiplier"]:
            message = "Missing input #6."
            return render_template("index.html", message=message, modules=modules, inverters=inverters)
=======
            message = "Enter a city:"
            return render_template("index.html", message=message)

        city_name = request.form["city"].title()

        ### OPEN WEATHER API ###
        API_KEY = "YOUR OPEN WEATHER API KEY"
        BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
        COMPLETE_URL = BASE_URL + "appid=" + API_KEY + "&q=" + city_name
        response = requests.get(COMPLETE_URL)
        data = response.json()

        # temperature conversion
        def k_2_c_f(k):
            """Converts Kelvin to Celsius and Fahrenheit."""
            c = k - 273.15
            f = c * (9/5) + 32

            return c, f

        # if city found
        if data["cod"] == 200:

            city = data["name"]
            country = data["sys"]["country"]
            lon = data["coord"]["lon"]
            lat = data["coord"]["lat"]
            date_current = str(dt.datetime.utcfromtimestamp(data["dt"]+data["timezone"])).split()[0]
            time_current = str(dt.datetime.utcfromtimestamp(data["dt"]+data["timezone"])).split()[1]
            time_sunrise = str(dt.datetime.utcfromtimestamp(data["sys"]["sunrise"]+data["timezone"])).split()[1]
            time_sunset = str(dt.datetime.utcfromtimestamp(data["sys"]["sunset"]+data["timezone"])).split()[1]

            description = data["weather"][0]["description"]
            temp = data["main"]["temp"] # K
            temp_c, temp_f = k_2_c_f(temp) # C/F
            temp_feels_like = data["main"]["feels_like"] # K
            temp_feels_like_c, temp_feels_like_f = k_2_c_f(temp_feels_like) # C/F
            temp_min = data["main"]["temp_min"] # K
            temp_min_c, temp_min_f = k_2_c_f(temp_min) # C/F
            temp_max = data["main"]["temp_max"] # K
            temp_max_c, temp_max_f = k_2_c_f(temp_max) # C/F
            humidity = data["main"]["humidity"] # %
            wind_speed = data["wind"]["speed"] # m/s

            # create dictionary for variables of interest
            data_dict ={
                "location": {
                "city": city,
                "country": country,
                "longitude": "%.2f" %lon,
                "latitude": "%.2f" %lat,
                },
                "datetime": {
                "current_date": date_current,
                "current_time": time_current,
                "sunrise_time": time_sunrise,
                "sunset_time": time_sunset,
                },
                "weather": {
                "description": description,
                "temperature": {
                "current_celsius": "%.2f" %temp_c,
                "current_fahrenheit": "%.2f" %temp_f,
                "current_feels_like_celsius": "%.2f" %temp_feels_like_c,
                "current_feels_like_fahrenheit": "%.2f" %temp_feels_like_f,
                "minimum_celsius": "%.2f" %temp_min_c,
                "minimum_fahrenheit": "%.2f" %temp_min_f,
                "maximum_celsius": "%.2f" %temp_max_c,
                "maximum_fahrenheit": "%.2f" %temp_max_f,
                },
                "humidity": humidity,
                "wind_speed": wind_speed,
                }
            }
            message = "City located!"
            line = "========================="
            link_image = f"https://www.google.com/search?q={city},%20{country}&tbm=isch&sxsrf=ALiCzsZ5M1itKyzlFbcGc14YxmoHngOfEg%3A1672276909102&source=hp&biw=1536&bih=714&ei=reusY6y_BMvgkPIP-42E2As&iflsig=AJiK0e8AAAAAY6z5vRFNQXZO4g5b2s1nmBSP9Lbp-PU3&ved=0ahUKEwjsyYb51J38AhVLMEQIHfsGAbsQ4dUDCAc&uact=5&oq=oslo&gs_lcp=CgNpbWcQAzIECCMQJzIFCAAQgAQyBQgAEIAEMgUIABCABDIICAAQgAQQsQMyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDoHCCMQ6gIQJzoICAAQsQMQgwFQiwRY3gZgmgpoAXAAeACAATOIAbwBkgEBNJgBAKABAaoBC2d3cy13aXotaW1nsAEK&sclient=img"
            
            return render_template("result.html", **data_dict, message=message, line=line, link_image=link_image)
>>>>>>> 7919e00f825a9d80769cabec39cca71bebc3902f
        
        # ensure typed inputs are valid
        try:
            float(request.form["tilt"])
        except ValueError:
            message = "Input #4 must be numeric."
            return render_template("index.html", message=message, modules=modules, inverters=inverters)
        if not (float(request.form["tilt"]) >= 0 and float(request.form["tilt"]) <= 90): 
            message = "Input #4 must be between 0 and 90."
            return render_template("index.html", message=message, modules=modules, inverters=inverters)
        try:
            float(request.form["azimuth"])
        except ValueError:
            message = "Input #5 must be numeric."
            return render_template("index.html", message=message, modules=modules, inverters=inverters)
        if not (float(request.form["azimuth"]) >= 0 and float(request.form["azimuth"]) <= 360): 
            message = "Input #5 must be between 0 and 360."
            return render_template("index.html", message=message, modules=modules, inverters=inverters)        
        try:
            int(request.form["multiplier"])
        except ValueError:
            message = "Input #6 must be an integer."
            return render_template("index.html", message=message, modules=modules, inverters=inverters)
        if int(request.form["multiplier"]) < 1: 
            message = "Input #6 must be at least 1."
            return render_template("index.html", message=message, modules=modules, inverters=inverters) 

        # query & assign input city
        city = request.form["city"].title()

        # data from API call
        data = open_weather_api(city)

        # city not found (return: message, messsage_null)
        if len(open_weather_clean_data(data)) == 2:
            message, _ = open_weather_clean_data(data)

            return render_template("index.html", message=message, modules=modules, inverters=inverters)

        # city found (return: data_dict, message, link_image)
        else:
            # for Weather Output
            data_dict, message, link_image, link_youtube = open_weather_clean_data(data)
            line = "========================="

            # for Solar Output
            module = request.form["modules"]
            inverter = request.form["inverters"]
            surface_tilt = float(request.form["tilt"])
            surface_azimuth = float(request.form["azimuth"])
            multiplier = int(request.form["multiplier"])

            system = {
                "module": module,
                "inverter": inverter,
                "surface_tilt": surface_tilt,
                "surface_azimuth": surface_azimuth,
                "multiplier": multiplier,
            }

            df = get_solar_production(city, module, inverter, surface_azimuth, surface_tilt, multiplier)
            monthly_production, total_production = get_monthly_production(df)
            plot = get_plot(monthly_production, city)
            
            
            return render_template("result.html", **data_dict, message=message, line=line, link_image=link_image, link_youtube=link_youtube, system=system, monthly_production=monthly_production, total_production=total_production, plot=plot.decode("utf-8"))

    # default page
    else:
        message = "Welcome!"
<<<<<<< HEAD
        return render_template("index.html", message=message, modules=modules, inverters=inverters)
=======
        return render_template("index.html", message=message)
>>>>>>> 7919e00f825a9d80769cabec39cca71bebc3902f
