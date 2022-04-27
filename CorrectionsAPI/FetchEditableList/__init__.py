import json
import logging
import os
import traceback
import pandas as pd

import azure.functions as func

from ..SharedFunctions import authenticator, db_connectors, global_vars


class FetchEditableList:
    def __init__(self, req):
        # get params from route
        self.version = req.route_params.get('version')

        # get token
        try:
            self.token = req.headers.__http_headers__["authorization"].split(" ")[
                1]
            self.token_missing = True if self.token is None else False
        except KeyError:
            self.token_missing = True

        # check for missing missing params
        if self.version == None:
            self.invalid_params = True
        else:
            self.invalid_params = False

        # authenticate
        self.authenticated, self.auth_response = authenticator.authenticate(
            self.token)

        # connect to dbs
        if self.authenticated:
            self.environment = os.environ.get('AZURE_FUNCTIONS_ENVIRONMENT')
            self.shadow_con, self.shadow_cur, self.shadow_engine = db_connectors.connect_to_shadow(
                self.environment)

    def fetch_editable_list(self):
        editable_list = pd.DataFrame(pd.read_sql(
            "SELECT editable_list, entry_to_iterate, iterator_editable_list, table_names FROM editable_list_by_version WHERE version = '{}'".format(self.version), self.shadow_engine))
        return editable_list

    def generate_editable_list(self):
        editable_list = self.fetch_editable_list()

        return_obj = {
            "editable_list": editable_list.iloc[0].get("editable_list"),
            "entry_to_iterate": editable_list.iloc[0].get("entry_to_iterate"),
            "iterator_editable_list": editable_list.iloc[0].get("iterator_editable_list"),
            "table_names": editable_list.iloc[0].get("table_names"),
        }

        if editable_list.empty:
            return func.HttpResponse(json.dumps({"message": "no version in shadow db"}), headers=global_vars.HEADER, status_code=400)
        else:
            return func.HttpResponse(json.dumps(return_obj), headers=global_vars.HEADER, status_code=200)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        editable_list_fetcher = FetchEditableList(req)

        if not editable_list_fetcher.authenticated:
            return func.HttpResponse(json.dumps(editable_list_fetcher.auth_response), headers=global_vars.HEADER, status_code=401)
        elif editable_list_fetcher.invalid_params:
            return func.HttpResponse("Missing query params", headers=global_vars.HEADER, status_code=400)
        elif editable_list_fetcher.token_missing:
            return func.HttpResponse("Token missing", headers=global_vars.HEADER, status_code=400)
        else:
            return editable_list_fetcher.generate_editable_list()

    except Exception:
        error = traceback.format_exc()
        logging.error(error)
        return func.HttpResponse(error, status_code=500)
