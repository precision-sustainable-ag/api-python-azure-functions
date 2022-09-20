import requests
import pandas as pd
import os

def  fetch_gdd(start_date, end_date, lat, lon, gddbase=10):
    api_key = os.environ["x-api-key"]
    api_header = {'x-api-key' : api_key}
    gdd_url= "https://api.precisionsustainableag.org/weather/daily"

    data = requests.get(
    gdd_url, params=
    {'lat':lat, 'lon':lon, 'start':start_date, 'end':end_date, 'stats':'sum(gdd)', 'gddbase':gddbase}, headers=api_header)

    return data.json()