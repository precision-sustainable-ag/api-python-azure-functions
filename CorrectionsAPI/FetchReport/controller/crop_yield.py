import pandas as pd
from ..services import crop_yield


def fetch_yield(site):
    mg_to_bushels = {
        "Corn": 0.000016,
        "Wheat": 0.000015,
        "Soybeans": 0.000015,
        "Cotton": 0.000028
    }
    resp, resp_status = crop_yield.req(site)
    if (resp_status):
        yield_data = pd.DataFrame(resp.json())
        bare_yield = None
        cover_yield = None
        if len(yield_data) > 0 and 'adjusted.grain.yield.Mg_ha' in yield_data.columns:
            if len(yield_data[yield_data['treatment'] == 'B']) > 0:
                bare_yield_data = yield_data[yield_data['treatment'] == 'B']
                if bare_yield_data.iloc[0]['adjusted.grain.yield.Mg_ha']:
                    bare_yield = bare_yield_data.iloc[0]['adjusted.grain.yield.Mg_ha']*mg_to_bushels[bare_yield_data.iloc[0]['cash.crop']]
            if len(yield_data[yield_data['treatment'] == 'C']) > 0:
                cover_yield_data = yield_data[yield_data['treatment'] == 'C']
                if cover_yield_data.iloc[0]['adjusted.grain.yield.Mg_ha']:
                    cover_yield = cover_yield_data.iloc[0]['adjusted.grain.yield.Mg_ha']*mg_to_bushels[cover_yield_data.iloc[0]['cash.crop']]
        return bare_yield, cover_yield
