import pandas as pd
import matplotlib.pyplot as plt
plt.switch_backend('agg')
from ..services import moisture


def plot_graph(vwc, file_name, start_date, end_date, depth="overall"):
    try:
        vwc['date'] = pd.to_datetime(vwc['timestamp'])
        newdf = (vwc.groupby(['treatment', pd.Grouper(
            key='date', freq='W')]).agg({'vwc': 'mean'}))
        newdf = newdf.reset_index()
        newdf['date'] = pd.to_datetime(newdf['date']).dt.date
        bare_df = newdf.loc[newdf['treatment'] == 'b']
        cover_df = newdf.loc[newdf['treatment'] == 'c']
        bare_df.sort_values(by=['date'], inplace=True)
        cover_df.sort_values(by=['date'], inplace=True)

        # newdf['date'] = pd.to_datetime(newdf['date']).dt.strftime('%m/%d/%Y')
        y_bare = bare_df['vwc'].to_list()
        y_cover = cover_df['vwc'].to_list()
        x_bare = bare_df['date'].to_list()
        x_cover = cover_df['date'].to_list()

        f = plt.figure()
        f.set_figwidth(6)
        f.set_figheight(3.75)
        # Plotting both the curves simultaneously
        plt.plot(x_bare, y_bare, color='y', label='Bare Ground')
        plt.plot(x_cover, y_cover, color='g', label='Cover crop')
        plt.gcf().autofmt_xdate()

        # Naming the x-axis, y-axis and the whole graph
        plt.xlabel("Week")
        plt.ylabel("Moisture(%)")
        plt.title("Moisture percentage at {depth} depth"
                .format(depth=depth))

        # Adding legend, which helps us recognize the curve according to it's color
        plt.legend()
        plt.savefig(file_name)
        plt.clf()
        plt.close()
    except Exception as e:
        print(e)

def fetch_vwc(start_date, end_date, site):
    resp, resp_status = moisture.req(start_date, end_date, site)
    if (resp_status):
        vwc_data = pd.DataFrame(resp.json())
        if len(vwc_data) != 0:
            vwc_overall = vwc_data

            plot_graph(vwc_overall, "FetchReport\\data\\MoistureGraph.png",
                       start_date, end_date)
            vwc_d = vwc_data[vwc_data["center_depth"] == -5]
            plot_graph(vwc_d, "FetchReport\\data\\MoistureGraphD.png",
                       start_date, end_date, str(-5))
            vwc_c = vwc_data[vwc_data["center_depth"] == -15]
            plot_graph(vwc_c, "FetchReport\\data\\MoistureGraphC.png",
                       start_date, end_date, str(-15))
            vwc_b = vwc_data[vwc_data["center_depth"] == -45]
            plot_graph(vwc_b, "FetchReport\\data\\MoistureGraphB.png",
                       start_date, end_date, str(-45))
            vwc_a = vwc_data[vwc_data["center_depth"] == -80]
            plot_graph(vwc_a, "FetchReport\\data\\MoistureGraphA.png",
                       start_date, end_date, str(-80))

            # vwc_d['date'] = pd.to_datetime(vwc_d['timestamp'])
            newdf = (vwc_d.groupby(['treatment', pd.Grouper(
                key='date', freq='W')]).agg({'soil_temp': 'mean'}))
            newdf = newdf.reset_index()
            newdf['date'] = pd.to_datetime(newdf['date']).dt.date
            bare_df = newdf.loc[newdf['treatment'] == 'b']
            cover_df = newdf.loc[newdf['treatment'] == 'c']
            bare_df.sort_values(by=['date'], inplace=True)
            cover_df.sort_values(by=['date'], inplace=True)

            # newdf['date'] = pd.to_datetime(newdf['date']).dt.strftime('%m/%d/%Y')
            bare_df['soil_temp'] = bare_df['soil_temp'].apply(
                lambda x: x*1.8 + 32)
            cover_df['soil_temp'] = cover_df['soil_temp'].apply(
                lambda x: x*1.8 + 32)
            y_bare = bare_df['soil_temp'].to_list()
            y_cover = cover_df['soil_temp'].to_list()
            x_bare = bare_df['date'].to_list()
            x_cover = cover_df['date'].to_list()


            # Plotting both the curves simultaneously
            plt.plot(x_bare, y_bare, color='y', label='Bare Ground')
            plt.plot(x_cover, y_cover, color='g', label='Cover crop')
            plt.gcf().autofmt_xdate()

            # Naming the x-axis, y-axis and the whole graph
            plt.xlabel("Week")
            plt.ylabel("Temperature in deg F")
            plt.title("Soil temperature at depth {depth}"
                      .format(depth=str(-5)))

            # Adding legend, which helps us recognize the curve according to it's color
            plt.legend()
            plt.savefig("FetchReport\\data\\TemperatureGraph.png")
            plt.clf()
            plt.close()
            # To load the display window

        return vwc_data
