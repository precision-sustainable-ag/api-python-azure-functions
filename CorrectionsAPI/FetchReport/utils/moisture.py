import os
import requests
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import math

def fetch_vwc(start_date, end_date, site):
    api_key = os.environ["x-api-key"]
    api_header = {'x-api-key' : api_key}
    precipitation_url= "https://api.precisionsustainableag.org/onfarm/soil_moisture"

    data = requests.get(
    precipitation_url, params=
    {'type':'tdr', 'start':start_date, 'end':end_date, 'code': site}, headers=api_header)

    vwc_data = pd.DataFrame(data.json())
    if len(vwc_data)!=0:
        vwc_temp = vwc_data
        vwc_temp['date'] = pd.to_datetime(vwc_temp['timestamp'])
        newdf = (vwc_temp.groupby(['treatment', pd.Grouper(key='date', freq='W')]).agg({'vwc':'mean'}))
        newdf = newdf.reset_index()
        newdf['date'] = pd.to_datetime(newdf['date']).dt.date
        bare_df = newdf.loc[newdf['treatment'] == 'b']
        cover_df = newdf.loc[newdf['treatment'] == 'c']
        bare_df.sort_values(by=['date'], inplace=True)
        cover_df.sort_values(by=['date'], inplace=True)

        # newdf['date'] = pd.to_datetime(newdf['date']).dt.strftime('%m/%d/%Y')
        y_bare = bare_df['vwc'].to_list()
        y_cover = cover_df['vwc'].to_list()
        x_bare = cover_df['date'].to_list()

        # Plotting both the curves simultaneously
        plt.plot(x_bare, y_bare, color='y', label='Bare Ground')
        plt.plot(x_bare, y_cover, color='g', label='Cover crop')
        plt.gcf().autofmt_xdate()

        # Naming the x-axis, y-axis and the whole graph
        plt.xlabel("Week")
        plt.ylabel("Moisture(%)")
        plt.title("Moisture percentage from {date1} to {date2} for site {site}"\
            .format(date1=start_date.strftime('%m/%d/%Y'),\
                 date2=end_date.strftime('%m/%d/%Y'), site = site))
        
        # Adding legend, which helps us recognize the curve according to it's color
        plt.legend()
        plt.savefig("FetchReport\\MoistureGraph.png")
        plt.clf()
        plt.close()
        # To load the display window

    return vwc_data