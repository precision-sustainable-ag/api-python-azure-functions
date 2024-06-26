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

        self.requested_site = self.route_params_obj.get("site")

    def fetch_site_information(self):
        try:
            api_key = os.environ["X_API_KEY"]
            api_header = {'Accept': 'application/json',
                'x-api-key': api_key, }
            biomass_url = 'https://api.precisionsustainableag.org/onfarm/raw'
            resp = requests.get(biomass_url, params={'table': 'site_information',\
                'code': self.route_params_obj.get("site"), 'output':'json'},\
                    headers=api_header)
            site_info = pd.DataFrame(resp.json())
            site_info = site_info[['code', 'affiliation', 'year', 'county', 'longitude', 'latitude', 'address']]
            return site_info, True

        except requests.exceptions.RequestException as e:
            print(e)
            return e, False
        
    def fetch_farm_history(self):
        try:
            api_key = os.environ["X_API_KEY"]
            api_header = {'Accept': 'application/json',
                'x-api-key': api_key, }
            biomass_url = 'https://api.precisionsustainableag.org/onfarm/raw'
            resp = requests.get(biomass_url, params={'table': 'farm_history',\
                'code': self.route_params_obj.get("site"), 'output':'json'},\
                    headers=api_header)
            farm_hist = pd.DataFrame(resp.json())
            farm_hist = farm_hist[['cc_planting_date', 'cc_termination_date', 'cash_crop_planting_date', 'cash_crop_harvest_date']]
            return farm_hist, True

        except requests.exceptions.RequestException as e:
            print(e)
            return e, False


    def generate_report(self):
        site_info, site_info_status = self.fetch_site_information()
        farm_hist, farm_hist_status = self.fetch_farm_history()

        if site_info_status and farm_hist_status and not site_info.empty and not farm_hist.empty:
            word_bytes = io.BytesIO()
            doc = assemble_doc.assemble(site_info, farm_hist, self.requested_site)

            # Save the document to a location/share as API response
            # file_name = 'SummaryReport'+self.requested_site+'.docx'
            doc.save(word_bytes)
            word_bytes.seek(0)
            return func.HttpResponse(
                word_bytes.read(),
                headers=global_vars.HEADER,
                status_code=201,
                mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        else:
            return func.HttpResponse(
                json.dumps({
                    "status": "error",
                    "details": "No site code in crown db"}),
                headers=global_vars.HEADER, status_code=400)
        


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
