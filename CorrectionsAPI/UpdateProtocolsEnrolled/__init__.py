import json
import logging
import os
import traceback

import azure.functions as func

from SharedFunctions import db_connectors, global_vars, initializer


class UpdateProtocolEnrollment:
    def __init__(self, req):
        initial_state = initializer.initialize(
            route_params=["code"], body_params=["protocols_enrolled"], req=req)

        self.route_params_obj = initial_state["route_params_obj"]
        self.body_params_obj = initial_state["body_params_obj"]
        self.token = initial_state["token"]
        self.token_missing = initial_state["token"] == None
        self.authenticated = initial_state["authenticated"]
        self.auth_response = initial_state["auth_response"]
        self.invalid_params = initial_state["route_params_obj"] is None or initial_state["body_params_obj"] is None

        # connect to dbs
        if self.authenticated:
            self.environment = os.environ.get('AZURE_FUNCTIONS_ENVIRONMENT')
            self.crown_con, self.crown_cur, self.crown_engine = db_connectors.connect_to_crown(
                self.environment)

    def update_producer(self):
        update_prod_query = "UPDATE site_information SET protocols_enrolled = %s WHERE code = %s"

        self.crown_cur.execute(
            update_prod_query, (self.body_params_obj["protocols_enrolled"], self.route_params_obj["code"]))

        if self.crown_cur.rowcount == 0:
            return func.HttpResponse(json.dumps({"status": "error", "details": "failed to update protocols_enrolled for code {} to {}".format(self.route_params_obj["code"], self.body_params_obj["protocols_enrolled"])}), headers=global_vars.HEADER, status_code=400)
        else:
            return func.HttpResponse(json.dumps({"status": "success", "details": "successfully updated protocols_enrolled for code {} to {}".format(self.route_params_obj["code"], self.body_params_obj["protocols_enrolled"])}), headers={'content-type': 'application/json'}, status_code=201)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        protocol_updater = UpdateProtocolEnrollment(req)

        # authenticate user based on token
        if any([not protocol_updater.authenticated, protocol_updater.invalid_params, protocol_updater.token_missing]):
            return initializer.get_response(protocol_updater.authenticated, protocol_updater.auth_response,
                                            protocol_updater.invalid_params, protocol_updater.token_missing, False)
        else:
            return protocol_updater.update_producer()

    except Exception as error:
        logging.info("program encountered exception: " +
                     traceback.format_exc())
        logging.exception(error)
        return func.HttpResponse(
            json.dumps({"status": "error", "details": traceback.format_exc()}),
            status_code=500,
            headers=global_vars.HEADER
        )
