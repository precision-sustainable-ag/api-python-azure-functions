import os
import requests


def req(site):
    try:
        api_key = os.environ["x-api-key"]
        api_header = {'x-api-key': api_key}
        biomass_url = "https://api.precisionsustainableag.org/onfarm/yield"
        resp = requests.get(
            biomass_url,
            params={'code': site},
            headers=api_header)
        return resp, True

    except requests.exceptions.RequestException as e:
        print(e)
        return e, False
