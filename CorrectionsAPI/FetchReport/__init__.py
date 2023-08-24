import json
import os
import logging
import traceback
import pandas as pd
import azure.functions as func
import io
import requests
# import asyncio
from SharedFunctions import db_connectors, global_vars, initializer
from .controller import assemble_doc


class FetchReport:
    def __init__(self, req):
        initial_state = initializer.initialize(
            route_params=["site"], body_params=None, req=req)

        self.route_params_obj = initial_state["route_params_obj"]
        self.token = initial_state["token"]
        self.token_missing = True if initial_state["token"] is None else False
        self.authenticated = initial_state["authenticated"]
        self.auth_response = initial_state["auth_response"]
        self.invalid_params = initial_state["route_params_obj"] is None

        # connect to dbs
        if self.authenticated:
            self.environment = os.environ.get('AZURE_FUNCTIONS_ENVIRONMENT')
            self.shadow_con, self.shadow_cur, self.shadow_engine = \
                db_connectors.connect_to_crown(self.environment)

        self.requested_site = self.route_params_obj.get("site")

    def fetch_site_info(self):
        try:
            api_key = os.environ["X_API_KEY"]
            api_header = {'Accept': 'application/json',
                'x-api-key': api_key, }
            biomass_url = 'https://api.precisionsustainableag.org/onfarm/raw'
            resp = requests.get(biomass_url, params={'table': 'site_information',\
                'code': self.route_params_obj.get("site"), 'output':'json'},\
                    headers=api_header)
            return resp, True

        except requests.exceptions.RequestException as e:
            print(e)
            return e, False

    def fetch_report_data(self):
        report_data = pd.DataFrame(pd.read_sql(
            "SELECT a.code, a.affiliation, a.county, a.longitude, a.latitude, \
                a.address, b.cc_planting_date, b.cc_termination_date, \
                    b.cash_crop_planting_date, b.cash_crop_harvest_date FROM \
                        site_information as a INNER JOIN farm_history as b \
                            ON a.code=b.code WHERE a.code = '{}'"
            .format(self.route_params_obj.get("site")), self.shadow_engine))
        return report_data

    def generate_report(self):
        print("HERE")
        site_info = self.fetch_site_info()
        print(site_info)


        '''
        report_data = self.fetch_report_data()

        
        if report_data.empty:
            return func.HttpResponse(
                json.dumps({
                    "status": "error",
                    "details": "No site code in crown db"}),
                headers=global_vars.HEADER, status_code=400)
        else:
            word_bytes = io.BytesIO()
            doc = assemble_doc.assemble(report_data, self.requested_site)

            # Save the document to a location/share as API response
            # file_name = 'SummaryReport'+self.requested_site+'.docx'
            doc.save(word_bytes)
            word_bytes.seek(0)
            return func.HttpResponse(
                word_bytes.read(),
                headers=global_vars.HEADER,
                status_code=201,
                mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        '''


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
