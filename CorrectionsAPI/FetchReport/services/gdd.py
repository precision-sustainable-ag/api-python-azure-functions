import os
import requests


def req(lat, lon, start_date, end_date, gddbase):
    try:
        api_key = os.environ["x_api_key"]
        api_header = {'x_api_key': api_key}
        gdd_url = "https://api.precisionsustainableag.org/weather/daily"
        resp = requests.get(
            gdd_url,
            params={
                'lat': lat, 'lon': lon, 'start': start_date, 'end': end_date,
                'stats': 'sum(gdd)', 'gddbase': gddbase},
            headers=api_header)
        return resp, True

    except requests.exceptions.RequestException as e:
        print(e)
        return e, False
