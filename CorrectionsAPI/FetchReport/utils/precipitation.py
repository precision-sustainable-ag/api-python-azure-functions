import requests
import pandas as pd
import os

def  fetch_precipitation(start_date, end_date, lat, lon):
    api_key = os.environ["x-api-key"]
    api_header = {'x-api-key' : api_key}
    precipitation_url= "https://api.precisionsustainableag.org/weather/daily"

    data = requests.get(
    precipitation_url, params=
    {'lat':lat, 'lon':lon, 'start':start_date, 'end':end_date, 'stats':'sum(precipitation)'}, headers=api_header)
    return data.json()
