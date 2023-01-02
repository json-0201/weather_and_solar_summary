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
        return render_template("index.html", message=message, modules=modules, inverters=inverters)