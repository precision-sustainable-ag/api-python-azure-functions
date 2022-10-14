import requests
import pandas as pd
import os


def fetch_nir(affiliation, site):

    api_key = os.environ["x-api-key"]
    api_header = {'x-api-key': api_key}
    biomass_url = "https://api.precisionsustainableag.org/onfarm/raw"

    data = requests.get(
        biomass_url, params={'table': "biomass_nir", 'affiliation': affiliation, 'code': site}, headers=api_header)

    nir = pd.DataFrame(data.json())
    nitrogen = None
    carbohydrates = None
    holo_cellulose = None
    lignin = None

    nitrogen = nir["percent_n_nir"].mean()
    carbohydrates = nir["percent_carb_nnorm"].mean()
    holo_cellulose = nir["percent_hemicell_calc"].mean()+nir["percent_cellulose_calc"].mean()
    lignin = nir["percent_lignin_norm"].mean()

    return nitrogen, carbohydrates, holo_cellulose, lignin
