from ..services import biomass
import pandas as pd
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import matplotlib.ticker as mticker



def fetch_biomass(affiliation, requested_site):

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

    affiliations = ",".join(region[aff_2_region[affiliation]])
    resp, resp_status = biomass.req(affiliations)
    if (resp_status):
        biomass_data = pd.DataFrame(resp.json())

        site_biomass = biomass_data[biomass_data['code'] == requested_site]
        if len(site_biomass) > 0 and \
                pd.notna(site_biomass.iloc[0].get('ash_corrected_cc_dry_biomass_kg_ha')):
            biomass_data['ash_corrected_cc_dry_biomass_lb_ac'] = (
                biomass_data['ash_corrected_cc_dry_biomass_kg_ha']*0.892179)
            site_year = site_biomass.iloc[0].get('year')
            biomass_data = biomass_data[biomass_data['year'] == site_year]
            biomass_data['Rank'] = (
                biomass_data['ash_corrected_cc_dry_biomass_lb_ac'].rank(ascending=1))
            biomass_data.sort_values(
                by=['ash_corrected_cc_dry_biomass_lb_ac'], inplace=True)
            site_biomass = (
                biomass_data.loc[biomass_data['code'] == requested_site])

            yaxis = biomass_data['ash_corrected_cc_dry_biomass_lb_ac'].to_list()
            xaxis = list(range(1, len(yaxis)+1))

            # create a figure and save the plot jpg image
            plt.figure()
            plt.scatter(xaxis, yaxis, color='black', alpha=0.5)
            plt.scatter(int(site_biomass.iloc[0].get("Rank")), site_biomass.iloc[0].get(
                "ash_corrected_cc_dry_biomass_lb_ac"), color='red', s=50)
            plt.text(int(site_biomass.iloc[0].get("Rank")), site_biomass.iloc[0].get(
                "ash_corrected_cc_dry_biomass_lb_ac"), requested_site)
            # plt.title("Biomass data for {reg} region in year {year}".format(reg=aff_2_region[affiliation], year=str(site_year)))
            plt.title("This is your farm's dry matter in comparison to all farms that use \n cover crops in our network in the {reg} region".format(
                reg=aff_2_region[affiliation]))
            plt.gca().xaxis.set_major_locator(mticker.MultipleLocator(2))
            plt.xlabel("Rank")
            plt.ylabel("Biomass produce in lbs/acre")
            plt.savefig("FetchReport\\data\\Graph.png")
            plt.clf()
            plt.close()
            return site_biomass.iloc[0].get("ash_corrected_cc_dry_biomass_lb_ac"), \
                site_biomass.iloc[0].get("cc_species")

        return None
