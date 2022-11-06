from ..controller import raw_nir, crop_yield, moisture
from ..controller import gdd, precipitation, hyperlink, biomass
import os
# from docx import Document
from docx.shared import Inches
import pandas as pd


def doc_header(doc):
    try:
        # header section
        # adding header with PSA logo
        section = doc.sections[0]
        header = section.header
        header_para = header.paragraphs[0]
        header_logo = header_para.add_run()
        header_logo.add_picture("FetchReport\\PSA.png", width=Inches(1))

        # footer
        footer = section.footer
        footer_para = footer.paragraphs[0]
        footer_para.add_run(
            'For questions about this report, ask: abc@xyz.com')
    except Exception as e:
        print(e)
    finally:
        return doc


def doc_farmDetails(doc, report_data):
    try:
        # Farm Name
        doc.add_heading('Farm Name:', 4)
        doc.add_paragraph().add_run(
            report_data.iloc[0].get("code"))

        # Farm Address
        doc.add_heading('Farm Address:', 4)
        doc.add_paragraph().add_run(
            report_data.iloc[0].get("address"))

        lat = round(report_data.iloc[0].get("latitude"), 4)
        lon = round(report_data.iloc[0].get("longitude"), 4)

        # Site Description
        doc.add_heading('Site Description:', 4)
        gps_para = doc.add_paragraph()
        gps_para.add_run('GPS Co-ordinates\n').itallic = True
        gps_para.add_run('Latitude: ')
        gps_para.add_run(str(lat))
        gps_para.add_run('\t')
        gps_para.add_run('Longitude: ')
        gps_para.add_run(str(lon))
        gps_para.add_run('\n')

        maps_link = "https://www.google.com/maps/search/{lat},{lon}"\
            .format(lat=lat, lon=lon)
        hyperlink.add_hyperlink(gps_para, maps_link, maps_link)
    except Exception as e:
        print(e)
    finally:
        return doc


def doc_cashcrop(doc, cash_planting, cash_harvest):
    try:
        cash_days = (cash_harvest-cash_planting).days \
            if (cash_planting is not None and cash_harvest is not None) else None
        doc.add_heading('Cash crop days:', 4)
        # Cash crop dates
        doc.add_paragraph('Date of planting Cash crop: ', style='List Bullet'
                          ).add_run(cash_planting.strftime("%m/%d/%Y") if cash_planting else "Not yet entered")
        doc.add_paragraph('Date of harvest Cash crop: ', style='List Bullet'
                          ).add_run(cash_harvest.strftime("%m/%d/%Y") if cash_harvest else "Not yet entered")
        doc.add_paragraph('Cash crop no of days in production: ', style='List Bullet'
                          ).add_run(str(cash_days) if cash_days else "________")

    except Exception as e:
        print(e)
    finally:
        return doc


def doc_covercrop(doc, cover_planting, cover_termination):
    try:
        cover_days = (cover_termination-cover_planting).days \
            if (cover_planting is not None and cover_termination is not None) else None
        doc.add_heading('Cover crop days:', 4)
        # Cover crop dates
        doc.add_paragraph('Date of planting Cover crop: ', style='List Bullet'
                          ).add_run(cover_planting.strftime("%m/%d/%Y") if cover_planting else "Not yet entered")
        doc.add_paragraph('Date of termination Cover crop: ', style='List Bullet'
                          ).add_run(cover_termination.strftime("%m/%d/%Y") if cover_termination else "Not yet entered")
        doc.add_paragraph('Cover crop no of days in production: ', style='List Bullet'
                          ).add_run(str(cover_days) if cover_days else "________")
    except Exception as e:
        print(e)
    finally:
        return doc


def doc_gdd(doc, cash_planting, cash_harvest, cover_planting, cover_termination, lat, lon):
    try:
        cash_gdd = gdd.fetch_gdd(cash_planting, cash_harvest, lat, lon, 10) \
            if (cash_planting is not None and cash_harvest is not None) else None
        cover_gdd = gdd.fetch_gdd(cover_planting, cover_termination, lat, lon, 4) \
            if (cover_planting is not None and cover_termination is not None) else None

        doc.add_heading('GDD:', 4)
        gdd_para = doc.add_paragraph(
            'GDD for Cover crop is ', style='List Bullet')
        gdd_para.add_run(
            str(round(cover_gdd[0]['sum(gdd)'], 1)) if cover_gdd else "________")
        gdd_para = doc.add_paragraph(
            'GDD for Cash crop is ', style='List Bullet')
        gdd_para.add_run(
            str(round(cash_gdd[0]['sum(gdd)'], 1)) if cash_gdd else "________")

    except Exception as e:
        print(e)
    finally:
        return doc


def doc_precipitation(doc, cash_planting, cash_harvest, cover_planting, cover_termination, lat, lon):
    try:
        cash_precipitation = precipitation.fetch_precipitation(cash_planting, cash_harvest, lat, lon) \
            if (cash_planting is not None and cash_harvest is not None) else None
        cover_precipitation = precipitation.fetch_precipitation(cover_planting, cover_termination, lat, lon) \
            if (cover_planting is not None and cover_termination is not None) else None

        doc.add_heading('Precipitation:', 4)
        # Precipitation
        preci_para = doc.add_paragraph(
            'Precipitation for Cover crop is ', style='List Bullet')
        preci_para.add_run(str(round(
            cover_precipitation[0]['sum(precipitation)'], 1))+" mm" if cover_precipitation else "________")
        preci_para = doc.add_paragraph(
            'Precipitation for Cash crop is ', style='List Bullet')
        preci_para.add_run(str(round(
            cash_precipitation[0]['sum(precipitation)'], 1))+" mm" if cash_precipitation else "________")

    except Exception as e:
        print(e)
    finally:
        return doc


def doc_biomass(doc, affilition, requested_site):
    try:
        site_biomass, species = biomass.fetch_biomass(affilition, requested_site)
        doc.add_heading('Cover crop species and biomass:', 4)
        species = species if species else "Unavailable"
        doc.add_paragraph('Cover crop species: ', style='List Bullet'
                          ).add_run(species)
        # Biomass and comparison
        site_biomass = str(round(site_biomass, 1)
                           ) if site_biomass else "Unavailable"
        doc.add_paragraph('Dry matter (lbs/acre):', style='List Bullet'
                          ).add_run(site_biomass)
        biomass_comp_para = doc.add_paragraph('Dry matter in comparison to others in the region:' +
                                              ' \n', style='List Bullet')
        if os.path.exists("FetchReport\\data\\Graph.png"):
            doc.add_picture("FetchReport\\data\\Graph.png")
        else:
            biomass_comp_para.add_run("Comparison not available")

    except Exception as e:
        print(e)
    finally:
        return doc


def doc_cropquality(doc, affilition, requested_site):
    try:
        nitrogen, carbohydrates, holo_cellulose, lignin = raw_nir.fetch_nir(
            affilition, requested_site)
        doc.add_heading('Cover crop quality:', 4)
        doc.add_paragraph('% Nitrogen: ', style='List Bullet'
                          ).add_run(str(round(nitrogen, 2)))
        doc.add_paragraph('% Carbohydrates: ', style='List Bullet'
                          ).add_run(str(round(carbohydrates, 2)))
        doc.add_paragraph('% Holo-cellulose: ', style='List Bullet'
                          ).add_run(str(round(holo_cellulose, 2)))
        doc.add_paragraph('% Lignin: ', style='List Bullet'
                          ).add_run(str(round(lignin, 2)))

    except Exception as e:
        print(e)
    finally:
        return doc


def doc_yield(doc, requested_site):
    try:
        bare_yield, cover_yield = crop_yield.fetch_yield(requested_site)
        doc.add_heading('Yield:', 4)
        yield_para = doc.add_paragraph('Bare Ground: ', style='List Bullet')
        yield_para.add_run(
            str(bare_yield)+" Mg/ha" if bare_yield else "Not available")
        yield_para = doc.add_paragraph('Cover: ', style='List Bullet')
        yield_para.add_run(
            str(cover_yield)+" Mg/ha" if cover_yield else "Not available")

    except Exception as e:
        print(e)
    finally:
        return doc


def doc_vwc(doc, requested_site, cash_planting, cash_harvest):
    try:
        vwc = moisture.fetch_vwc(cash_planting, cash_harvest, requested_site)\
            if (cash_planting is not None) else None
        # if (cash_planting is not None and cash_harvest is not None) else None
        vwc_dict = {}
        if vwc.size != 0:
            vwc['date'] = pd.to_datetime(vwc['timestamp'])
            new_df = (vwc.groupby(['treatment', pd.Grouper(
                key='date', freq='W')]).agg({'vwc': 'mean'}))
            new_df = new_df.reset_index()
            new_df['date'] = pd.to_datetime(new_df['date']).dt.date
            new_df['date'] = pd.to_datetime(
                new_df['date']).dt.strftime('%m/%d/%Y')

            for i in range(len(new_df)):
                d = str(new_df.iloc[i].get('date'))
                if d not in vwc_dict.keys():
                    vwc_dict[d] = ["", ""]
                if str(new_df.iloc[i].get('treatment')) == "b":
                    vwc_dict[d][0] = str(round(new_df.iloc[i].get('vwc'), 3))
                elif str(new_df.iloc[i].get('treatment')) == "c":
                    vwc_dict[d][1] = str(round(new_df.iloc[i].get('vwc'), 3))

        doc.add_heading('Soil Temperature: ', 4)
        doc.add_paragraph('Temperature data: ', style='List Bullet')
        if os.path.exists("FetchReport\\data\\TemperatureGraph.png"):
            doc.add_picture("FetchReport\\data\\TemperatureGraph.png")
        if os.path.exists("FetchReport\\data\\TemperatureGraph.png"):
            os.remove("FetchReport\\data\\TemperatureGraph.png")

        #Water and Moisture
        doc.add_heading('Water and Moisture: ', 4)
        doc.add_paragraph('Moisture data: ', style='List Bullet')
        doc.add_paragraph('Cover crop vs bare: ', style='List Number 2').add_run(
            "Refer the table below for overall(avr) values")
        table = doc.add_table(rows=1, cols=3, style="Table Grid")
        row = table.rows[0].cells
        row[0].text = 'Week'
        row[1].text = 'Bare Ground'
        row[2].text = 'Cover Crop'

        for key, value in vwc_dict.items():
            # Adding a row and then adding data in it.
            row = table.add_row().cells
            # Converting id to string as table can only take string input
            row[0].text = key
            row[1].text = value[0]
            row[2].text = value[1]

        if os.path.exists("FetchReport\\data\\MoistureGraph.png"):
            doc.add_picture("FetchReport\\data\\MoistureGraph.png")
        if os.path.exists("FetchReport\\data\\MoistureGraphD.png"):
            doc.add_picture("FetchReport\\data\\MoistureGraphD.png")
        if os.path.exists("FetchReport\\data\\MoistureGraphC.png"):
            doc.add_picture("FetchReport\\data\\MoistureGraphC.png")
        if os.path.exists("FetchReport\\data\\MoistureGraphB.png"):
            doc.add_picture("FetchReport\\data\\MoistureGraphB.png")
        if os.path.exists("FetchReport\\data\\MoistureGraphA.png"):
            doc.add_picture("FetchReport\\data\\MoistureGraphA.png")

        if os.path.exists("FetchReport\\data\\MoistureGraph.png"):
            os.remove("FetchReport\\data\\MoistureGraph.png")
        if os.path.exists("FetchReport\\data\\MoistureGraphD.png"):
            os.remove("FetchReport\\data\\MoistureGraphD.png")
        if os.path.exists("FetchReport\\data\\MoistureGraphC.png"):
            os.remove("FetchReport\\data\\MoistureGraphC.png")
        if os.path.exists("FetchReport\\data\\MoistureGraphB.png"):
            os.remove("FetchReport\\data\\MoistureGraphB.png")
        if os.path.exists("FetchReport\\data\\MoistureGraphA.png"):
            os.remove("FetchReport\\data\\MoistureGraphA.png")

        if os.path.exists("FetchReport\\data\\Graph.png"):
            os.remove("FetchReport\\data\\Graph.png")
        if os.path.exists("FetchReport\\data\\MoistureGraph.png"):
            os.remove("FetchReport\\data\\MoistureGraph.png")

    except Exception as e:
        print(e)
    finally:
        return doc
