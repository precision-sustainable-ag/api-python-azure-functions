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
    bare_yield = None
    cover_yield = None
    print(yield_data)
    if len(yield_data)>0:
        if len(yield_data[yield_data['treatment']=='B'])>0:
            bare_yield_data = yield_data[yield_data['treatment']=='B']
            if bare_yield_data.iloc[0]['adjusted.grain.yield.Mg_ha']:
                bare_yield = bare_yield_data.iloc[0]['adjusted.grain.yield.Mg_ha']
        if len(yield_data[yield_data['treatment']=='C'])>0:
            cover_yield_data = yield_data[yield_data['treatment']=='C']
            if cover_yield_data.iloc[0]['adjusted.grain.yield.Mg_ha']:
                cover_yield = cover_yield_data.iloc[0]['adjusted.grain.yield.Mg_ha']
    # print(yield_data)
    return bare_yield, cover_yield
