import os
import requests
import pandas as pd
import os

def fetch_vwc(start_date, end_date, site):
    api_key = os.environ["x-api-key"]
    api_header = {'x-api-key' : api_key}
    precipitation_url= "https://api.precisionsustainableag.org/onfarm/soil_moisture"

    data = requests.get(
    precipitation_url, params=
    {'type':'tdr', 'start':start_date, 'end':end_date, 'code': site}, headers=api_header)

    vwc_data = pd.DataFrame(data.json())

    return vwc_data