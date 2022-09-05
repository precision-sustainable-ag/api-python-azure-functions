import json
import logging
import requests
import os
import traceback
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt
import azure.functions as func
from datetime import datetime, timezone
import matplotlib.pyplot as plt 

from SharedFunctions import db_connectors, global_vars, initializer


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

    def fetch_biomass(self):
        api_key = os.environ["x-api-key"]
        api_header = {'x-api-key' : api_key}
        biomass_url= "https://api.precisionsustainableag.org/onfarm/biomass"

        # request biomass data
        biomass_data = requests.get(
        biomass_url, params={'affiliation':'NC'}, headers=api_header)
        print(type(biomass_data))
        report_data = pd.DataFrame(biomass_data.json())
        report_data['biomass_mean'] = report_data[['uncorrected_cc_dry_biomass_kg_ha', 'ash_corrected_cc_dry_biomass_kg_ha']].mean(axis=1)
        report_data.sort_values(by=['biomass_mean'], inplace=True)
        report_data['biomass_mean'].fillna(0)
        yaxis=report_data['biomass_mean'].to_list()
        # first = biomass_data.json()
        print(len(yaxis))
        print(yaxis)
        x = list(range(1,len(yaxis)+1))
        plt.plot(yaxis, x)
        plt.xlabel('x - axis') 
        # naming the y axis 
        plt.ylabel('y - axis') 
            
        # giving a title to my graph 
        plt.title('My first graph!') 
        plt.savefig("output.jpg")
        # print(report_data.head(10))
        return biomass_data

    def fetch_report(self):
        report_data = pd.DataFrame(pd.read_sql(
            "SELECT a.code, a.affiliation, a.county, a.longitude, a.latitude, a.address, b.cc_planting_date, b.cc_termination_date, b.cash_crop_planting_date, b.cash_crop_harvest_date FROM site_information as a INNER JOIN farm_history as b ON a.code=b.code WHERE a.code = '{}'".format(self.route_params_obj.get("site")), self.shadow_engine))
        return report_data

    def generate_report(self):
        report_data = self.fetch_report()
        self.fetch_biomass()
        print(report_data)

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
            gpsPara.add_run(str(report_data.iloc[0].get("latitude")))
            gpsPara.add_run('\t')
            gpsPara.add_run('Longitude: ')
            gpsPara.add_run(str(report_data.iloc[0].get("longitude")))
            gpsPara.add_run('\n (Google maps link)')

            #Dates this report summarizes
            doc.add_heading('Dates this report summarizes:', 3)
            currentDate = datetime.now()
            print(currentDate)
            date = doc.add_paragraph(str(currentDate))

            #Summary of Activities and Management
            doc.add_heading('Summary of Activities and Management:', 3)
            # activitesPara = doc.add_paragraph()
            doc.add_paragraph('Date of planting cash crop: ', style='List Bullet').add_run(str(report_data.iloc[0].get("cash_crop_planting_date")))
            doc.add_paragraph('Date of harvest cash crop: ', style='List Bullet').add_run(str(report_data.iloc[0].get("cash_crop_harvest_date")))
            doc.add_paragraph('Total GDD: ', style='List Bullet')
            doc.add_paragraph('Total precipitation: ', style='List Bullet')

            #Cover Crop
            doc.add_heading('Cover Crop:', 3)
            # coverCropPara = doc.add_paragraph()
            doc.add_paragraph('Date of planting- Cover: ', style='List Bullet').add_run(str(report_data.iloc[0].get("cc_planting_date")))
            doc.add_paragraph('Date of termination- Cover: ', style='List Bullet').add_run(str(report_data.iloc[0].get("cc_termination_date")))
            doc.add_paragraph('Biomass: ', style='List Bullet')
            doc.add_paragraph('Biomass in comparison to others in the region: ', style='List Bullet')
            doc.add_paragraph('Yield in the bare and cover: ', style='List Bullet')

            #Water and Moisture
            doc.add_heading('Water and Moisture: ', 3)
            doc.add_paragraph('Moisture data: ', style='List Bullet')
            doc.add_paragraph('Cover crop vs bare: ', style='List Number 2')


            #Decision Support Tools
            doc.add_heading('Decision Support Tools:', 3)
            dstPara = doc.add_paragraph()
            dstPara.add_run('The Decision Support Tools (DSTs) are designed for farmers'+
            ' to input their data and receive custom generated information on how to '+
            'address their management strategies. The Cover Crop Nitrogen Calculator '+
            '(CC-NCALC) calculates the amount of nitrogen available after the planting '+
            'and termination of a cover crop. ')
            
            # now save the document to a location
            doc.save('SummaryReport.docx')
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
