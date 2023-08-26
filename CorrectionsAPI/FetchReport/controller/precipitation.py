from ..services import precipitation


def fetch_precipitation(start_date, end_date, lat, lon):
    resp, resp_status = precipitation.req(lat, lon, start_date, end_date)
    if (resp_status):
        return resp.json()
