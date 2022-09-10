import json
import os
import logging
from turtle import color
import requests
import os
import traceback
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt
import azure.functions as func
from datetime import datetime, timedelta, timezone
import matplotlib.pyplot as plt 

from SharedFunctions import db_connectors, global_vars, initializer
from FetchReport import biomass, moisture, precipitation, crop_yield

class FetchReport:
    def __init__(self, req):
        initial_state = initializer.initialize(
            route_params=["site"], body_params=None, req=req)

        self.route_params_obj = initial_state["route_params_obj"]
        self.token = initial_state["token"]
        self.token_missing = initial_state["token"] == None
        self.authenticated = initial_state["authenticated"]
        self.auth_response = initial_state["auth_response"]
        self.invalid_params = initial_state["route_params_obj"] is None

        # connect to dbs
        if self.authenticated:
            self.environment = os.environ.get('AZURE_FUNCTIONS_ENVIRONMENT')
            self.shadow_con, self.shadow_cur, self.shadow_engine = db_connectors.connect_to_crown(
                self.environment)

        self.region = {
            "Northeast":["PA", "VT", "NH"],
            "Southeast":["AL", "FL", "GA", "NC"],
            "Mid-Atlantic":["DE", "MD", "VA", "VAWest"],
            "Midwest":["IN", "KS", "NE", "Indigo", "AR"],
        }
        self.aff_2_region = {
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

        self.requested_site = self.route_params_obj.get("site")

    def fetch_report(self):
        report_data = pd.DataFrame(pd.read_sql(
            "SELECT a.code, a.affiliation, a.county, a.longitude, a.latitude, "+
            "a.address, b.cc_planting_date, b.cc_termination_date, "+
            "b.cash_crop_planting_date, b.cash_crop_harvest_date FROM "+
            "site_information as a INNER JOIN farm_history as b ON a.code=b.code"+
            " WHERE a.code = '{}'".format(self.route_params_obj.get("site")), self.shadow_engine))
        return report_data

    def generate_report(self):
        # os.remove("FetchReport\\Graph.png")
        # os.remove("FetchReport\\vwc_tdrA_b.png")
        report_data = self.fetch_report()

        planting_cash = report_data.iloc[0].get("cash_crop_planting_date")
        harvest_cash = report_data.iloc[0].get("cash_crop_harvest_date")
        if not harvest_cash: harvest_cash = planting_cash + timedelta(days=60)

        planting_cover = report_data.iloc[0].get("cc_planting_date")
        termination_cover = report_data.iloc[0].get("cc_termination_date")
        if not termination_cover: termination_cover =  planting_cover + timedelta(days=60)

        dates = [planting_cash, harvest_cash,planting_cover, termination_cover]
        min_date = min(d for d in dates if d is not None)
        max_date = max(d for d in dates if d is not None)
        lat = report_data.iloc[0].get("latitude")
        lon = report_data.iloc[0].get("longitude")

        site_biomass = biomass.fetch_biomass(self.region[self.aff_2_region[report_data.iloc[0].get("affiliation")]], self.requested_site)
        site_yield = crop_yield.fetch_yield(self.requested_site)
        site_precipitation = precipitation.fetch_precipitation(min_date, max_date, lat, lon)
        vwc = moisture.fetch_vwc(planting_cash, harvest_cash, self.requested_site)
        vwc_dict = {}
        if vwc.size != 0:
            vwc['date'] = pd.to_datetime(vwc['timestamp'])
            newdf = (vwc.groupby(['treatment', pd.Grouper(key='date', freq='W')]).agg({'vwc':'mean'}))
            newdf = newdf.reset_index()
            newdf['date'] = pd.to_datetime(newdf['date']).dt.date
            print(newdf)

            for i in range(len(newdf)):
                d = str(newdf.iloc[i].get('date'))
                print(d)
                if d not in vwc_dict.keys():
                    vwc_dict[d] = ["", ""]
                if str(newdf.iloc[i].get('treatment')) == "b":
                    vwc_dict[d][0] = str(round(newdf.iloc[i].get('vwc'), 3))
                elif str(newdf.iloc[i].get('treatment')) == "c":
                    vwc_dict[d][1] = str(round(newdf.iloc[i].get('vwc'), 3))

        precipitation_cash_df = site_precipitation.loc[(site_precipitation['date'] >= planting_cash) & (site_precipitation['date'] <= harvest_cash)]
        precipitation_cover_df = site_precipitation.loc[(site_precipitation['date'] >= planting_cover) & (site_precipitation['date'] <= termination_cover)]
        precipitation_cash = precipitation_cash_df['precipitation'].sum()
        precipitation_cover = precipitation_cover_df['precipitation'].sum()

        if report_data.empty:
            return func.HttpResponse(json.dumps({"status": "error", "details": "no site code in crown db"}), headers=global_vars.HEADER, status_code=400)
        else:
            doc = Document()

            #header section
            #adding header with PSA logo
            section = doc.sections[0]
            header = section.header
            headerPara = header.paragraphs[0]
            headerLogo = headerPara.add_run()
            headerLogo.add_picture("FetchReport\\PSA.png", width=Inches(1))

            #footer
            footer = section.footer
            footerPara = footer.paragraphs[0]
            footerPara.add_run('For any grievances reaach us at : abc@xyz.com')

            #PSA paragraph
            psaPara = doc.add_paragraph('\n'+'The Precision Sustainable Agriculture (PSA)'+ 
            'On-Farm network deploys common research protocols that study the short-term'+
            ' effects of cover crops on farms that currently use cover crops. '+
            'By utilizing farms with different management practices, the data collected'+
            ' can account for a wide range of factors such as termination timing, specific selections, and climate impacts. '+
            'The data is used to build tools to aid in site-specific management decisions.\n')

            #Farm Name
            doc.add_heading('Farm Name:', 3)
            farmName = doc.add_paragraph().add_run(report_data.iloc[0].get("code"))

            #Farm Address
            doc.add_heading('Farm Address:', 3)
            farmAdd = doc.add_paragraph().add_run(report_data.iloc[0].get("address"))

            #Site Description
            doc.add_heading('Site Description:', 3)
            gpsPara = doc.add_paragraph()
            gpsPara.add_run('GPS Co-ordinates\n').itallic=True
            gpsPara.add_run('Latitude: ')
            gpsPara.add_run(str(lat))
            gpsPara.add_run('\t')
            gpsPara.add_run('Longitude: ')
            gpsPara.add_run(str(lon))
            gpsPara.add_run('\n (Google maps link)')

            #Dates this report summarizes
            doc.add_heading('Dates this report summarizes:', 3)
            currentDate = datetime.now()
            print(currentDate)
            date = doc.add_paragraph(str(currentDate))

            #Summary of Activities and Management
            doc.add_heading('Summary of Activities and Management:', 3)
            # activitesPara = doc.add_paragraph()
            doc.add_paragraph('Date of planting cash crop: ', style='List Bullet'
            ).add_run(str(report_data.iloc[0].get("cash_crop_planting_date")))
            doc.add_paragraph('Date of harvest cash crop: ', style='List Bullet'
            ).add_run(str(report_data.iloc[0].get("cash_crop_harvest_date")))
            doc.add_paragraph('Total GDD: ', style='List Bullet')
            preci_para = doc.add_paragraph('Total precipitation: ', style='List Bullet')
            preci_para.add_run("\nTotal precipitation for Cash crop from "+
            str(planting_cash)+" to "+str(harvest_cash)+" was "+str(round(precipitation_cash, 3))+" mm")
            preci_para.add_run("\nTotal precipitation for Cover crop from "+
            str(planting_cover)+" to "+str(termination_cover)+" was "+str(round(precipitation_cover, 3))+" mm")
            #Cover Crop
            doc.add_heading('Cover Crop:', 3)
            # coverCropPara = doc.add_paragraph()
            doc.add_paragraph('Date of planting- Cover: ', style='List Bullet'
            ).add_run(str(report_data.iloc[0].get("cc_planting_date")))
            doc.add_paragraph('Date of termination- Cover: ', style='List Bullet'
            ).add_run(str(report_data.iloc[0].get("cc_termination_date")))
            doc.add_paragraph('Biomass (kg/ha): ', style='List Bullet'
            ).add_run(str(site_biomass.iloc[0].get("biomass_mean")))
            biomass_comp_para = doc.add_paragraph('Biomass in comparison to others in the region:'+
            ' \n', style='List Bullet')
            if os.path.exists("FetchReport\\Graph.png"):
                doc.add_picture("FetchReport\\Graph.png")
            else:
                biomass_comp_para.add_run("Comparison not available")

            yield_MgHa = "Not available"
            if len(site_yield)>0:
                yield_MgHa = str(site_yield.iloc[0].get("adjusted.grain.yield.Mg_ha"))
            doc.add_paragraph('Yield in the bare and cover (Mg/ha): ', style='List Bullet'
            ).add_run(yield_MgHa)

            #Water and Moisture
            doc.add_heading('Water and Moisture: ', 3)
            doc.add_paragraph('Moisture data: ', style='List Bullet')
            doc.add_paragraph('Cover crop vs bare: ', style='List Number 2').add_run("Refer the table below")
            table = doc.add_table(rows=1, cols=3)
            row = table.rows[0].cells
            row[0].text = 'Week'
            row[1].text = 'Treatment B'
            row[2].text = 'Treatment C'
            # doc.add_picture("FetchReport\\vwc_tdrA_b.png")
            for key, value in vwc_dict.items():
            
                # Adding a row and then adding data in it.
                row = table.add_row().cells
                # Converting id to string as table can only take string input
                row[0].text = key
                row[1].text = value[0]
                row[2].text = value[1]


            #Decision Support Tools
            doc.add_heading('Decision Support Tools:', 3)
            dstPara = doc.add_paragraph()
            dstPara.add_run('The Decision Support Tools (DSTs) are designed for farmers'+
            ' to input their data and receive custom generated information on how to '+
            'address their management strategies. The Cover Crop Nitrogen Calculator '+
            '(CC-NCALC) calculates the amount of nitrogen available after the planting '+
            'and termination of a cover crop. ')
            
            # now save the document to a location
            file_name = 'SummaryReport'+self.requested_site+'.docx'
            doc.save(file_name)
            if os.path.exists("FetchReport\\Graph.png"):
                os.remove("FetchReport\\Graph.png")
            return_obj = {
                "status": "success",
                "details": "successfully fetched report data for {}".format(self.route_params_obj.get("site")),
                "json_response": "response obtained from fetch query {}".format(report_data),
            }

            return func.HttpResponse(json.dumps(return_obj), headers=global_vars.HEADER, status_code=201)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        report_data_fetcher = FetchReport(req)

        # authenticate user based on token
        if any([not report_data_fetcher.authenticated, report_data_fetcher.invalid_params, report_data_fetcher.token_missing]):
            return initializer.get_response(report_data_fetcher.authenticated, report_data_fetcher.auth_response,
                                            report_data_fetcher.invalid_params, report_data_fetcher.token_missing, False)
        else:
            return report_data_fetcher.generate_report()

    except Exception as error:
        logging.info("program encountered exception: " +
                     traceback.format_exc())
        logging.exception(error)
        return func.HttpResponse(
            json.dumps({"status": "error", "details": traceback.format_exc()}),
            status_code=500,
            headers=global_vars.HEADER
        )
