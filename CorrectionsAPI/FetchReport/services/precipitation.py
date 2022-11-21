import os
import requests


def req(lat, lon, start_date, end_date):
    try:
        api_key = os.environ["X_API_KEY"]
        api_header = {'x-api-key': api_key}
        precipitation_url = "https://api.precisionsustainableag.org/weather/daily"
        resp = requests.get(precipitation_url,\
            params={'lat': lat, 'lon': lon, 'start': start_date,\
                'end': end_date, 'stats': 'sum(precipitation)'},\
                    headers=api_header)
        return resp, True

    except requests.exceptions.RequestException as e:
        print(e)
        return e, False
