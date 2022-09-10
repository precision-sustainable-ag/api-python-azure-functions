import requests
import pandas as pd
import os

def fetch_yield(site):
    
    api_key = os.environ["x-api-key"]
    api_header = {'x-api-key' : api_key}
    biomass_url= "https://api.precisionsustainableag.org/onfarm/yield"

    data = requests.get(
    biomass_url, params={'code':site}, headers=api_header)

    yield_data = pd.DataFrame(data.json())
    # print(yield_data)
    return yield_data
