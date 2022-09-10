import requests
import matplotlib.pyplot as plt 
import pandas as pd
import os

def fetch_biomass(affiliation, requested_site):
    api_key = os.environ["x-api-key"]
    api_header = {'x-api-key' : api_key}
    biomass_url= "https://api.precisionsustainableag.org/onfarm/biomass"
    affiliations = ",".join(affiliation)

    # request biomass data
    data = requests.get(
    biomass_url, params={'affiliation':affiliations}, headers=api_header)

    biomass_data = pd.DataFrame(data.json())
    biomass_data['biomass_mean'] = biomass_data[['uncorrected_cc_dry_biomass_kg_ha',
            'ash_corrected_cc_dry_biomass_kg_ha']].mean(axis=1)
    biomass_data = biomass_data[biomass_data['biomass_mean'].notna()]

#     biomass_data = biomass_data[biomass_data['ash_corrected_cc_dry_biomass_kg_ha'].notna()]

    biomass_data['Rank'] = biomass_data['biomass_mean'].rank(ascending = 1)
    biomass_data.sort_values(by=['biomass_mean'], inplace=True)
    site_biomass = biomass_data.loc[biomass_data['code'] == requested_site]

    yaxis = biomass_data['biomass_mean'].to_list()
    xaxis = list(range(1,len(yaxis)+1))
    
    ## create a figure and save the plot jpg image
    # fig = plt.figure(figsize=(6,6))
    plt.figure(1)
    # plt.subplot(211)
    plt.scatter(xaxis, yaxis, color='black', alpha=0.5)
    plt.scatter(int(site_biomass.iloc[0].get("Rank")), site_biomass.iloc[0].get("biomass_mean"), color='red', s=100)
    plt.text(int(site_biomass.iloc[0].get("Rank"))-1, site_biomass.iloc[0].get("biomass_mean")+2, requested_site)
    plt.xlabel("Rank")
    plt.ylabel("Biomass produce in kg_ha")
    plt.savefig("FetchReport\\Graph.png")
    plt.clf()

    # fig.savefig("FetchReport\\Graph.png")
    return site_biomass
