import pandas as pd
from ..services import crop_yield
import matplotlib.ticker as mticker
import io
import matplotlib.pyplot as plt
plt.switch_backend('agg')


def fetch_yield(site_info, requested_site):

    region = {
        "Northeast": ["PA", "VT", "NH"],
        "Southeast": ["AL", "FL", "GA", "NC"],
        "Mid-Atlantic": ["DE", "MD", "VA", "VAWest"],
        "Midwest": ["IN", "KS", "NE", "Indigo", "AR"],
    }
    aff_2_region = {
        "PA": "Northeast",
        "VT": "Northeast",
        "NH": "Northeast",
        "AL": "Southeast",
        "FL": "Southeast",
        "GA": "Southeast",
        "NC": "Southeast",
        "DE": "Mid-Atlantic",
        "MD": "Mid-Atlantic",
        "VA": "Mid-Atlantic",
        "VAWest": "Mid-Atlantic",
        "IN": "Midwest",
        "KS": "Midwest",
        "NE": "Midwest",
        "Indigo": "Midwest",
        "AR": "Midwest",
    }
    mg_to_bushels = {
        "Corn": 16,
        "Wheat": 15,
        "Soybeans": 15,
        "Cotton": 28
    }

    affiliation = site_info.iloc[0].get("affiliation")
    year = site_info.iloc[0].get("year")

    affiliations = ",".join(region[aff_2_region[affiliation]])
    resp, resp_status = crop_yield.req(affiliations)
    if (resp_status):
        yield_data = pd.DataFrame(resp.json())
        yield_data = yield_data[yield_data['year'] == year]
        yield_data = yield_data[yield_data['adjusted.grain.yield.Mg_ha'].notna()]
        
        yield_data['adjusted.grain.yield.bushels_acre'] = None
        for index, row in yield_data.iterrows():
            yield_data.loc[index, 'adjusted.grain.yield.bushels_acre'] = int(row['adjusted.grain.yield.Mg_ha']) * mg_to_bushels[row['cash.crop']]

        site_yield = (yield_data.loc[yield_data['code'] == requested_site]) # contains treatments b and c
        site_yield['treatment'] = site_yield['treatment'].apply(lambda x: x.strip())

        codes = list(yield_data.code.unique())
        average_yields = pd.DataFrame(columns = ['code', 'average'])
        for code in codes:
            yields = yield_data[yield_data['code'] == code]
            average = yields.loc[:, 'adjusted.grain.yield.bushels_acre'].mean()
            average_yields.loc[len(average_yields.index)] = [code, average] 
        
        average_yields['Rank'] = (average_yields['average'].rank(ascending=1))
        average_yields.sort_values(by=['average'], inplace=True)

        site_row = (average_yields.loc[average_yields['code'] == requested_site])
        site_rank = site_row['Rank'].iloc[0] if not site_row.empty else None
        average_yields = (average_yields.loc[average_yields['code'] != requested_site])

        xaxis = average_yields["Rank"].tolist()
        yaxis = average_yields["average"].tolist()

        figure = io.BytesIO()

        
        plt.figure()
        main = plt.scatter(xaxis, yaxis, alpha=0.5, facecolors='none', edgecolors='black')
        plt.ylabel("Adjusted Grain Yield in bushels/acre")
        plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(2))
        plt.margins(x=0.1, y=0.1)
        plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False) 
            
        if site_rank:
            bare_yield = site_yield[site_yield['treatment'] == 'B']['adjusted.grain.yield.bushels_acre'].iloc[0]
            cover_yield = site_yield[site_yield['treatment'] == 'C']['adjusted.grain.yield.bushels_acre'].iloc[0]
            cash_crop = site_yield.iloc[0]['cash.crop']
            bare = plt.scatter(site_rank, bare_yield, marker='s', facecolors='none', edgecolors='black', s=50)
            cover = plt.scatter(site_rank, cover_yield, marker='s', color='black', s=50)
            plt.legend((main, bare, cover),('Other Farms', 'Bare', 'Cover Crop'),scatterpoints=1, loc='lower right')
            plt.title("This is your Farm's Adjusted Grain Yield in Comparison to All Farms \n in the {reg} Region".format(reg=aff_2_region[affiliation]))
            plt.savefig(figure)
            plt.clf()
            plt.close()
            return bare_yield, cover_yield, cash_crop, figure
        else:
            plt.title("This is the Adjusted Grain Yield of all Farms that use Cover Crops in our Network in the {reg} Region".format(reg=aff_2_region[affiliation]))
            plt.savefig(figure)
            plt.clf()
            plt.close()
            return None, None, None, figure
            
    return None, None, None, None
        
    