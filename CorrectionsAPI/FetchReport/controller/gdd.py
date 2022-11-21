from ..services import gdd


def fetch_gdd(start_date, end_date, lat, lon, gddbase=10):
    resp, resp_status = gdd.req(lat, lon, start_date, end_date, gddbase)
    if (resp_status):
        return resp.json()
