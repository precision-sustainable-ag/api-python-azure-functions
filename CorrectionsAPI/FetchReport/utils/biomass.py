from cmath import nan
import site
import requests
import matplotlib.pyplot as plt 
import pandas as pd
import os

def fetch_biomass(affiliation, requested_site):

    region = {
        "Northeast":["PA", "VT", "NH"],
        "Southeast":["AL", "FL", "GA", "NC"],
        "Mid-Atlantic":["DE", "MD", "VA", "VAWest"],
        "Midwest":["IN", "KS", "NE", "Indigo", "AR"],
    }
    aff_2_region = {
        "PA":"Northeast",
        "VT":"Northeast",
        "NH":"Northeast",
        "AL":"Southeast",
        "FL":"Southeast",
        "GA":"Southeast",
        "NC":"Southeast",
        "DE":"Mid-Atlantic",
        "MD":"Mid-Atlantic",
        "VA":"Mid-Atlantic",
        "VAWest":"Mid-Atlantic",
        "IN":"Midwest",
        "KS":"Midwest",
        "NE":"Midwest",
        "Indigo":"Midwest",
        "AR":"Midwest",
    }

    api_key = os.environ["x-api-key"]
    api_header = {'x-api-key' : api_key}
    biomass_url= "https://api.precisionsustainableag.org/onfarm/biomass"
    affiliations = ",".join(region[aff_2_region[affiliation]])
    # request biomass data
    data = requests.get(
    biomass_url, params={'affiliation':affiliations}, headers=api_header)

    biomass_data = pd.DataFrame(data.json())
    # biomass_data['biomass_mean'] = biomass_data[['uncorrected_cc_dry_biomass_kg_ha',
    #         'ash_corrected_cc_dry_biomass_kg_ha']].mean(axis=1)
    # biomass_data = biomass_data[biomass_data['biomass_mean'].notna()]

    site_biomass = biomass_data[biomass_data['code'] == requested_site]
    print(site_biomass.iloc[0].get('ash_corrected_cc_dry_biomass_kg_ha'))
    if len(site_biomass)>0 and pd.notna(site_biomass.iloc[0].get('ash_corrected_cc_dry_biomass_kg_ha')):
        biomass_data['ash_corrected_cc_dry_biomass_lb_ac'] = biomass_data['ash_corrected_cc_dry_biomass_kg_ha']*0.892179
        site_year = site_biomass.iloc[0].get('year')
        biomass_data = biomass_data[biomass_data['year']==site_year]
        biomass_data['Rank'] = biomass_data['ash_corrected_cc_dry_biomass_lb_ac'].rank(ascending = 1)
        biomass_data.sort_values(by=['ash_corrected_cc_dry_biomass_lb_ac'], inplace=True)
        site_biomass = biomass_data.loc[biomass_data['code'] == requested_site]

        yaxis = biomass_data['ash_corrected_cc_dry_biomass_kg_ha'].to_list()
        xaxis = list(range(1,len(yaxis)+1))
            
        ## create a figure and save the plot jpg image
        # fig = plt.figure(figsize=(6,6))
        plt.figure(1)
        # plt.subplot(211)
        plt.scatter(xaxis, yaxis, color='black', alpha=0.5)
        plt.scatter(int(site_biomass.iloc[0].get("Rank")), site_biomass.iloc[0].get("ash_corrected_cc_dry_biomass_lb_ac"), color='red', s=100)
        plt.text(int(site_biomass.iloc[0].get("Rank")), site_biomass.iloc[0].get("ash_corrected_cc_dry_biomass_lb_ac"), requested_site)
        # plt.title("Biomass data for {reg} region in year {year}".format(reg=aff_2_region[affiliation], year=str(site_year)))
        plt.title("This is your farm's dry matter in comparison to all farms that use \n cover crops in our network in the {reg} region".format(reg=aff_2_region[affiliation]))
        plt.xlabel("Rank")
        plt.ylabel("Biomass produce in lbs/acre")
        plt.savefig("FetchReport\\Graph.png")
        plt.clf()
        plt.close()
        return site_biomass.iloc[0].get("ash_corrected_cc_dry_biomass_lb_ac"), \
            site_biomass.iloc[0].get("cc_species")

    return None
