import io
from ..services import moisture
import pandas as pd
import matplotlib.pyplot as plt
plt.switch_backend('agg')


def plot_graph(vwc, file_name, start_date, end_date, depth="overall"):
    try:
        fig = io.BytesIO()
        vwc['date'] = pd.to_datetime(vwc['timestamp'])
        new_df = (vwc.groupby(['treatment', pd.Grouper(
            key='date', freq='W')]).agg({'vwc': 'mean'}))
        new_df = new_df.reset_index()
        new_df['date'] = pd.to_datetime(new_df['date']).dt.date
        bare_df = new_df.loc[new_df['treatment'] == 'b']
        cover_df = new_df.loc[new_df['treatment'] == 'c']
        bare_df.sort_values(by=['date'], inplace=True)
        cover_df.sort_values(by=['date'], inplace=True)

    # new_df['date'] = pd.to_datetime(new_df['date']).dt.strftime('%m/%d/%Y')
        y_bare = bare_df['vwc'].to_list()
        y_cover = cover_df['vwc'].to_list()
        x_bare = bare_df['date'].to_list()
        x_cover = cover_df['date'].to_list()

        f = plt.figure()
        f.set_figwidth(6)
        f.set_figheight(3.75)
        # Plotting both the curves simultaneously
        plt.plot(x_bare, y_bare, color='black', linestyle='dashed', label='Bare Ground')
        plt.plot(x_cover, y_cover, color='black', label='Cover Crop')
        plt.gcf().autofmt_xdate()

        # Naming the x-axis, y-axis and the whole graph
        plt.ylabel("Soil Moisture(%)")
        plt.ylim(0, 50)
        if depth == "overall":
            plt.title("Average Soil Moisture Percentage from Surface to 40 inches")
        else:
            plt.title("Soil Moisture Percentage at {depth} Depth".format(depth=depth))

        # Adding legend, which helps us recognize curve according to it's color
        plt.legend()
        plt.savefig(fig)
        # plt.savefig(file_name)
        plt.clf()
        plt.close()
        return fig
    except Exception as e:
        print(e)


def fetch_vwc(start_date, end_date, site):
    resp, resp_status = moisture.req(start_date, end_date, site)
    if (resp_status):
        vwc_data = pd.DataFrame(resp.json())
        vwc_data = vwc_data[vwc_data['vwc']<=100]
        if len(vwc_data) != 0:
            vwc_overall = vwc_data

            fig_moisture = plot_graph(vwc_overall, "FetchReport/data/SoilMoistureGraph.png",
                                      start_date, end_date)
            vwc_d = vwc_data[vwc_data["center_depth"] == -5]
            fig_moisture_D = plot_graph(vwc_d, "FetchReport/data/SoilMoistureGraphD.png",
                                        start_date, end_date, "surface")
            vwc_c = vwc_data[vwc_data["center_depth"] == -15]
            fig_moisture_C = plot_graph(vwc_c, "FetchReport/data/SoilMoistureGraphC.png",
                                        start_date, end_date, "6 inch")
            vwc_b = vwc_data[vwc_data["center_depth"] == -45]
            fig_moisture_B = plot_graph(vwc_b, "FetchReport/data/SoilMoistureGraphB.png",
                                        start_date, end_date, "18 inch")
            vwc_a = vwc_data[vwc_data["center_depth"] == -80]
            fig_moisture_A = plot_graph(vwc_a, "FetchReport/data/SoilMoistureGraphA.png",
                                        start_date, end_date, "31 inch")

            # vwc_d['date'] = pd.to_datetime(vwc_d['timestamp'])
            new_df = (vwc_d.groupby(['treatment', pd.Grouper(
                key='date', freq='W')]).agg({'soil_temp': 'mean'}))
            new_df = new_df.reset_index()
            new_df['date'] = pd.to_datetime(new_df['date']).dt.date
            bare_df = new_df.loc[new_df['treatment'] == 'b']
            cover_df = new_df.loc[new_df['treatment'] == 'c']
            bare_df.sort_values(by=['date'], inplace=True)
            cover_df.sort_values(by=['date'], inplace=True)

        # new_df['date']=pd.to_datetime(new_df['date']).dt.strftime('%m/%d/%Y')
            bare_df['soil_temp'] = bare_df['soil_temp'].apply(
                lambda x: x*1.8 + 32)
            cover_df['soil_temp'] = cover_df['soil_temp'].apply(
                lambda x: x*1.8 + 32)
            y_bare = bare_df['soil_temp'].to_list()
            y_cover = cover_df['soil_temp'].to_list()
            x_bare = bare_df['date'].to_list()
            x_cover = cover_df['date'].to_list()

            # Plotting both the curves simultaneously
            plt.plot(x_bare, y_bare, color='black', linestyle='dashed', label='Bare Ground')
            plt.plot(x_cover, y_cover, color='black', label='Cover crop')
            plt.gcf().autofmt_xdate()

            # Naming the x-axis, y-axis and the whole graph
            plt.ylabel("Temperature in °F")
            plt.title("Soil Temperature at Surface")

            plt.legend()
            fig_temp = io.BytesIO()
            plt.savefig(fig_temp)
            # plt.savefig("FetchReport/data/TemperatureGraph.png")
            plt.clf()
            plt.close()
            # To load the display window

        return vwc_data, fig_temp, fig_moisture, fig_moisture_D, fig_moisture_C, fig_moisture_B, fig_moisture_A
