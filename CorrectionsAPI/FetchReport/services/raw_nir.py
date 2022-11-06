import os
import requests


def req(affiliation, site):
    try:
        api_key = os.environ["x_api_key"]
        api_header = {'Accept': 'application/json',
            'x-api-key': api_key, }
        biomass_url = 'https://api.precisionsustainableag.org/onfarm/raw'
        resp = requests.get(biomass_url, params={'table': 'biomass_nir',\
            'affiliation': affiliation, 'code': site, 'output':'json'},\
                headers=api_header)
        return resp, True

    except requests.exceptions.RequestException as e:
        print(e)
        return e, False
