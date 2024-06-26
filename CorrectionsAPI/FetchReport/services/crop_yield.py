import os
import requests


def req(affiliations):
    try:
        api_key = os.environ["X_API_KEY"]
        api_header = { 'Accept': 'application/json',
                'x-api-key': api_key, }
        biomass_url = "https://api.precisionsustainableag.org/onfarm/yield"
        resp = requests.get(biomass_url, params={'affiliation': affiliations, 'output':'json'},\
                headers=api_header)
        return resp, True

    except requests.exceptions.RequestException as e:
        print(e)
        return e, False
