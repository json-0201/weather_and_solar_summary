# import libraries
import numpy as np, pandas as pd
import requests, datetime as dt
import pvlib
from timezonefinder import TimezoneFinder
from typing import Tuple


def k_2_c_f(k: float) -> float:
    """Converts Kelvin to Celsius and Fahrenheit."""
    c = k - 273.15
    f = c * (9/5) + 32

    return c, f


def parse_url(city: str, country: str) -> str:
    """Returns parsed URL text for: 'city, country'."""

    text = f"{city}, {country}"
    text = text.replace(" ", "%20").replace(",", "%2C")

    return text


def open_weather_api(city: str) -> dict:
    """Returns data via API call for Open Weather"""

    API_KEY = "337b00a1e423612843a73ec31e09053b"
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
    COMPLETE_URL = BASE_URL + "appid=" + API_KEY + "&q=" + city
    response = requests.get(COMPLETE_URL)
    data = response.json()

    return data


def open_weather_clean_data(data: dict) -> Tuple[dict, str]:
    """Returns cleaned data from API call for Open Weather."""

    # city found
    if data["cod"] == 200:
        
        # convert Kelvin to Celsius and Fahrenheit
        temp_c, temp_f = k_2_c_f(data["main"]["temp"])
        temp_feels_like_c, temp_feels_like_f = k_2_c_f(data["main"]["feels_like"])
        temp_min_c, temp_min_f = k_2_c_f(data["main"]["temp_min"])
        temp_max_c, temp_max_f = k_2_c_f(data["main"]["temp_max"])

        # create dictionary for variables of interest
        data_dict ={
            "location": {
            "city": data["name"],
            "country": data["sys"]["country"],
            "longitude": "%.2f" %data["coord"]["lon"],
            "latitude": "%.2f" %data["coord"]["lat"],
            },
            "datetime": {
            "current_date": str(dt.datetime.utcfromtimestamp(data["dt"]+data["timezone"])).split()[0],
            "current_time": str(dt.datetime.utcfromtimestamp(data["dt"]+data["timezone"])).split()[1],
            "sunrise_time": str(dt.datetime.utcfromtimestamp(data["sys"]["sunrise"]+data["timezone"])).split()[1],
            "sunset_time": str(dt.datetime.utcfromtimestamp(data["sys"]["sunset"]+data["timezone"])).split()[1],
            },
            "weather": {
            "description": data["weather"][0]["description"],
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
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            }
        }

        message = "City located!"
        parsed_url = parse_url(data["name"], data["sys"]["country"])
        link_image = f"https://www.google.com/search?q={parsed_url}&tbm=isch&sxsrf=ALiCzsZ5M1itKyzlFbcGc14YxmoHngOfEg%3A1672276909102&source=hp&biw=1536&bih=714&ei=reusY6y_BMvgkPIP-42E2As&iflsig=AJiK0e8AAAAAY6z5vRFNQXZO4g5b2s1nmBSP9Lbp-PU3&ved=0ahUKEwjsyYb51J38AhVLMEQIHfsGAbsQ4dUDCAc&uact=5&oq=oslo&gs_lcp=CgNpbWcQAzIECCMQJzIFCAAQgAQyBQgAEIAEMgUIABCABDIICAAQgAQQsQMyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDoHCCMQ6gIQJzoICAAQsQMQgwFQiwRY3gZgmgpoAXAAeACAATOIAbwBkgEBNJgBAKABAaoBC2d3cy13aXotaW1nsAEK&sclient=img"
        link_youtube = f"https://www.youtube.com/results?search_query={parsed_url}"


        return data_dict, message, link_image, link_youtube
    
    # city not found
    else:

        message = "City not found, try again!"
        message_null = ""

        return message, message_null


def get_location(city: str) -> tuple:
    """Returns a tuple containing: latitude, longitude, name, altitude, timezone"""

    # city name
    name = city.title()
    
    # latitude, longitude from Open Weather API
    latitude = open_weather_api(city)["coord"]["lat"]
    longitude = open_weather_api(city)["coord"]["lon"]

    # Google - Elevation API
    API_KEY = "AIzaSyAMmlL1Eo8HVEHJVxF9xsDZZx5JukK4glY"
    BASE_URL = "https://maps.googleapis.com/maps/api/elevation/json"
    COMPLETE_URL = BASE_URL + "?locations=" + str(latitude) + "%2C" + str(longitude) + "&key=" + API_KEY
    response = requests.get(COMPLETE_URL).json()
    altitude = response["results"][0]["elevation"]

    # timezone
    tf = TimezoneFinder()
    timezone = tf.timezone_at(lat=latitude, lng=longitude)

    return latitude, longitude, name, altitude, timezone


def get_tmy(city: str) -> tuple:
    """Returns the coordinates of a city."""

    latitude, longitude, _, _, _ = get_location(city)
    tmy = pvlib.iotools.get_pvgis_tmy(latitude, longitude, map_variables=True)[0]
    tmy.index.name = "utc_time"

    return tmy


def get_solar_production(city, module, inverter, surface_azimuth, surface_tilt, multiplier):
    """Simulates solar production per user input and returns results of interest."""

    # system defined per user input
    mod = pvlib.pvsystem.retrieve_sam("SandiaMod")[module]
    inv = pvlib.pvsystem.retrieve_sam("cecinverter")[inverter]
    temp_model_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"]["open_rack_glass_glass"]
    system = {
        "module": mod, "inverter": inv,
        "surface_tilt": surface_tilt, "surface_azimuth": surface_azimuth
        }

    # location, weather information
    latitude, longitude, name, altitude, timezone = get_location(city)
    tmy = get_tmy(city)

    # PV-calculation
    solpos = pvlib.solarposition.get_solarposition(
        time=tmy.index,
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        temperature=tmy["temp_air"],
        pressure=pvlib.atmosphere.alt2pres(altitude),
    )
    dni_extra = pvlib.irradiance.get_extra_radiation(tmy.index)
    airmass = pvlib.atmosphere.get_relative_airmass(solpos['apparent_zenith'])
    pressure = pvlib.atmosphere.alt2pres(altitude)
    am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)
    aoi = pvlib.irradiance.aoi(
        system['surface_tilt'],
        system['surface_azimuth'],
        solpos["apparent_zenith"],
        solpos["azimuth"],
    )
    total_irradiance = pvlib.irradiance.get_total_irradiance(
        system['surface_tilt'],
        system['surface_azimuth'],
        solpos['apparent_zenith'],
        solpos['azimuth'],
        tmy['dni'],
        tmy['ghi'],
        tmy['dhi'],
        dni_extra=dni_extra,
        model='haydavies',
    )
    cell_temperature = pvlib.temperature.sapm_cell(
        total_irradiance['poa_global'],
        tmy["temp_air"],
        tmy["wind_speed"],
        **temp_model_params,
    )
    effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(
        total_irradiance['poa_direct'],
        total_irradiance['poa_diffuse'],
        am_abs,
        aoi,
        mod,
    )
    dc = pvlib.pvsystem.sapm(effective_irradiance, cell_temperature, mod)
    ac = pvlib.inverter.sandia(dc['v_mp'], dc['p_mp'], inv)

    df = ac.to_frame().reset_index()
    df.columns = ["utc_time","production"]
    df["production"] *= multiplier

    return df


def get_monthly_production(data) -> dict:
    """Returns monthly PV output from the pvlib simulation."""
    
    total_production = int(data["production"].sum())

    months = ["1","2","3","4","5","6","7","8","9","10","11","12"]

    monthly_data = {}
    for mon, ind in zip(months, range(1, 13)):
        monthly_data[mon] = data.loc[data["utc_time"].dt.month == ind]

    monthly_production = {}
    for mon, ind in zip(months, range(1, 13)):
        monthly_production[mon] = int(monthly_data[f"{ind}"]["production"].sum())

    return monthly_production, total_production


def get_plot(data: dict, city: str):
    """Generates a plot for year-long propduction, by month"""

    import matplotlib.pyplot as plt
    import os, base64, io
    from PIL import Image

    x = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    y = list(map(int, list(data.values())))
    print([(mon, str(prod)+" Whr") for mon, prod in zip(x, y)]) 

    plt.plot(x, y, "-or")
    plt.title(f"PV Production in {city}")
    plt.ylabel("Whr")

    os.chdir("/mnt/c/Users/Jimmy Son/Desktop/CS/Python/projects/weather_and_solar_summary/website/static")
    plt.savefig("production.png")
    
    im = Image.open("production.png")
    im = im.convert("RGB")
    data = io.BytesIO()
    im.save(data, "JPEG")
    encoded_img_data = base64.b64encode(data.getvalue())
    
    return encoded_img_data


def get_modules_inverters() -> list:
    """Returns lists of Sandia modules & CEC inverters."""

    modules_full = pd.DataFrame(pvlib.pvsystem.retrieve_sam("SandiaMod"))
    modules_name = modules_full.columns.tolist()

    inverters_full = pd.DataFrame(pvlib.pvsystem.retrieve_sam("cecinverter"))
    inverters_name = inverters_full.columns.tolist()

    return modules_name, inverters_name


def get_temperature_model() -> list:
    """Returns a list of temperature models."""

    models = list(pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"].keys())

    return models