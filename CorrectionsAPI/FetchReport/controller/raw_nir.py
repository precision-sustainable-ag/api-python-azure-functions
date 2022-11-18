import pandas as pd
import asyncio
from ..services import raw_nir


async def fetch_nir(affiliation, site):
    resp, resp_status = await raw_nir.req(affiliation, site)
    if (resp_status):
        nir = pd.DataFrame(resp.json())
        nitrogen = None
        carbohydrates = None
        holo_cellulose = None
        lignin = None

        nitrogen = nir["percent_n_nir"].mean()
        carbohydrates = nir["percent_carb_nnorm"].mean()
        holo_cellulose = nir["percent_hemicell_calc"].mean(
        )+nir["percent_cellulose_calc"].mean()
        lignin = nir["percent_lignin_norm"].mean()

    return nitrogen, carbohydrates, holo_cellulose, lignin
