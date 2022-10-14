import os
import requests


def req(start_date, end_date, site):
    try:
        api_key = os.environ["x-api-key"]
        api_header = {'x-api-key': api_key}
        moisture_url = "https://api.precisionsustainableag.org/onfarm/soil_moisture"
        resp = requests.get(
            moisture_url,
            params={
                'type': 'tdr', 'start': start_date, 'end': end_date, 'code': site},
            headers=api_header)
        return resp, True

    except requests.exceptions.RequestException as e:
        print(e)
        return e, False
