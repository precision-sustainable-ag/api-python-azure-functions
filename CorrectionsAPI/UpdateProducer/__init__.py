import json
import logging
import os
import traceback

import azure.functions as func

from SharedFunctions import authenticator, db_connectors, global_vars, initializer


class SubmitNewEntry:
    def __init__(self, req):
        initial_state = initializer.initilize(
            route_params=["producer_id", "code"], body_params=None, req=req)

        self.route_params_obj = initial_state["route_params_obj"]
        self.token = initial_state["token"]
        self.token_missing = initial_state["token"] == None
        self.authenticated = initial_state["authenticated"]
        self.auth_response = initial_state["auth_response"]
        self.invalid_params = initial_state["route_params_obj"] is None

        # connect to dbs
        if self.authenticated:
            self.environment = os.environ.get('AZURE_FUNCTIONS_ENVIRONMENT')
            self.crown_con, self.crown_cur, self.crown_engine = db_connectors.connect_to_crown(
                self.environment)

    def update_producer(self):
        sql_string = "UPDATE site_information SET producer_id = %s WHERE code = %s"

        try:
            self.crown_cur.execute(
                sql_string, (self.route_params_obj["producer_id"], self.route_params_obj["code"]))
            return func.HttpResponse(json.dumps({"status": "success", "details": "successfully updated producer {} to be code {}".format(self.route_params_obj["producer_id"], self.route_params_obj["code"])}), headers={'content-type': 'application/json'}, status_code=201)
        except Exception:
            return func.HttpResponse(json.dumps({"status": "error", "details": "failed to update producer"}), headers=global_vars.HEADER, status_code=400)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        producer_updater = SubmitNewEntry(req)

        # authenticate user based on token
        if any([not producer_updater.authenticated, producer_updater.invalid_params, producer_updater.token_missing]):
            return initializer.get_response(producer_updater.authenticated, producer_updater.auth_response,
                                            producer_updater.invalid_params, producer_updater.token_missing, False)
        else:
            return producer_updater.update_producer()

    except Exception as error:
        logging.info("program encountered exception: " +
                     traceback.format_exc())
        logging.exception(error)
        return func.HttpResponse(
            json.dumps({"status": "error", "details": traceback.format_exc()}),
            status_code=500,
            headers=global_vars.HEADER
        )
