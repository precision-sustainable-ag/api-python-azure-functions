import io
import matplotlib.ticker as mticker
from ..services import biomass
import pandas as pd
import matplotlib.pyplot as plt
plt.switch_backend('agg')



def fetch_biomass(site_info, requested_site):

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

    affiliation = site_info.iloc[0].get("affiliation")
    year = site_info.iloc[0].get("year")

    affiliations = ",".join(region[aff_2_region[affiliation]])
    resp, resp_status = biomass.req(affiliations)
    if (resp_status):
        biomass_data = pd.DataFrame(resp.json())
        biomass_data = biomass_data[biomass_data['year'] == year]
        biomass_data = biomass_data[biomass_data['uncorrected_cc_dry_biomass_kg_ha'].notna()]
        biomass_data['uncorrected_cc_dry_biomass_lb_ac'] = (biomass_data['uncorrected_cc_dry_biomass_kg_ha']*0.892179)
        biomass_data['Rank'] = (biomass_data['uncorrected_cc_dry_biomass_lb_ac'].rank(ascending=1))
        biomass_data.sort_values(by=['uncorrected_cc_dry_biomass_lb_ac'], inplace=True)
        site_biomass = (biomass_data.loc[biomass_data['code'] == requested_site])
        biomass_data = (biomass_data.loc[biomass_data['code'] != requested_site])

        xaxis = biomass_data["Rank"].tolist()
        yaxis = biomass_data["uncorrected_cc_dry_biomass_lb_ac"].tolist()

        figure = io.BytesIO()

        plt.figure()
        plt.scatter(xaxis, yaxis, alpha=0.5, facecolors='none', edgecolors='black')
            
        for index, row in site_biomass.iterrows():
            plt.scatter(int(row['Rank']), row["uncorrected_cc_dry_biomass_lb_ac"], color='black', s=50)
            pointText = requested_site + "\n" + "Dry Matter: " + str(round(row["uncorrected_cc_dry_biomass_lb_ac"]))
            plt.text(int(row['Rank'])+0.4, row["uncorrected_cc_dry_biomass_lb_ac"]-800, pointText)
            
        plt.ylabel("Biomass in lbs/acre")
        plt.margins(x=0.1, y=0.1)
        plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(2))
        plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False) 

        if len(site_biomass.index)>0:
            plt.title("This is your farm's cover crop dry matter in comparison to all farms that \n use cover crops in our network in the {reg} region".format(reg=aff_2_region[affiliation]))
            plt.savefig(figure)
            plt.clf()
            plt.close()
            return site_biomass[["uncorrected_cc_dry_biomass_lb_ac"]], site_biomass[["cc_species"]], figure
        else:
            plt.title("This is the cover crop dry matter of all farms that use cover crops in our network in the {reg} region".format(reg=aff_2_region[affiliation]))
            plt.savefig(figure)
            plt.clf()
            plt.close()
            return None, None, figure
    return None, None, None
        
    