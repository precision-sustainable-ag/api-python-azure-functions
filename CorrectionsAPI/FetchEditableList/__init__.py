import json
import logging
import os
import traceback
import pandas as pd

import azure.functions as func

from SharedFunctions import authenticator, db_connectors, global_vars, initializer


class FetchEditableList:
    def __init__(self, req):
        initial_state = initializer.initilize(
            route_params=["version"], body_params=None, req=req)

        self.route_params_obj = initial_state["route_params_obj"]
        self.token = initial_state["token"]
        self.token_missing = initial_state["token"] == None
        self.authenticated = initial_state["authenticated"]
        self.auth_response = initial_state["auth_response"]
        self.invalid_params = initial_state["route_params_obj"] is None

        # connect to dbs
        if self.authenticated:
            self.environment = os.environ.get('AZURE_FUNCTIONS_ENVIRONMENT')
            self.shadow_con, self.shadow_cur, self.shadow_engine = db_connectors.connect_to_shadow(
                self.environment)

    def fetch_editable_list(self):
        editable_list = pd.DataFrame(pd.read_sql(
            "SELECT editable_list, entry_to_iterate, iterator_editable_list, table_names FROM editable_list_by_version WHERE version = '{}'".format(self.route_params_obj.get("version")), self.shadow_engine))
        return editable_list

    def generate_editable_list(self):
        editable_list = self.fetch_editable_list()

        print(editable_list)

        if editable_list.empty:
            return func.HttpResponse(json.dumps({"status": "error", "details": "no version in shadow db"}), headers=global_vars.HEADER, status_code=400)
        else:
            return_obj = {
                "status": "success",
                "details": "successfully fetched editable list for {}".format(self.route_params_obj.get("version")),
                "editable_list": editable_list.iloc[0].get("editable_list"),
                "entry_to_iterate": editable_list.iloc[0].get("entry_to_iterate"),
                "iterator_editable_list": editable_list.iloc[0].get("iterator_editable_list"),
                "table_names": editable_list.iloc[0].get("table_names"),
            }

            return func.HttpResponse(json.dumps(return_obj), headers=global_vars.HEADER, status_code=201)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        editable_list_fetcher = FetchEditableList(req)

        # authenticate user based on token
        if any([not editable_list_fetcher.authenticated, editable_list_fetcher.invalid_params, editable_list_fetcher.token_missing]):
            return initializer.get_response(editable_list_fetcher.authenticated, editable_list_fetcher.auth_response,
                                            editable_list_fetcher.invalid_params, editable_list_fetcher.token_missing, False)
        else:
            return editable_list_fetcher.generate_editable_list()

    except Exception as error:
        logging.info("program encountered exception: " +
                     traceback.format_exc())
        logging.exception(error)
        return func.HttpResponse(
            json.dumps({"status": "error", "details": traceback.format_exc()}),
            status_code=500,
            headers=global_vars.HEADER
        )
