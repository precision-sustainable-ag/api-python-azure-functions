import os
import requests
import traceback


def req(site):
    try:
        api_key = os.environ["X_API_KEY"]
        api_header = { 'Accept': 'application/json',
                'x-api-key': api_key, }
        biomass_url = "https://api.precisionsustainableag.org/onfarm/yield"
        resp = requests.get(biomass_url, params={'code': site},\
            headers=api_header)
        return resp, True

    except requests.exceptions.RequestException as e:
        traceback.print_exc()
        return e, False
