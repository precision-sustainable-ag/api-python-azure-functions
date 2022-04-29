import json
import logging
import os
import traceback

import azure.functions as func

from ..SharedFunctions import authenticator, db_connectors, global_vars


class SubmitNewEntry:
    def __init__(self, req):
        # get params from route
        self.producer_id = req.route_params.get('producer_id')
        self.code = req.route_params.get('code')

        # get token
        try:
            self.token = req.headers.__http_headers__["authorization"].split(" ")[
                1]
            self.token_missing = True if self.token is None else False
        except KeyError:
            self.token_missing = True

        # check for missing missing params
        if None in [self.producer_id, self.code]:
            self.invalid_params = True
        else:
            self.invalid_params = False

        # authenticate
        self.authenticated, self.auth_response = authenticator.authenticate(
            self.token)

        # connect to dbs
        if self.authenticated:
            self.environment = os.environ.get('AZURE_FUNCTIONS_ENVIRONMENT')
            self.crown_con, self.crown_cur, self.crown_engine = db_connectors.connect_to_crown(
                self.environment)

    def update_producer(self):
        sql_string = "UPDATE site_information SET producer_id = %s WHERE code = %s"
        self.crown_cur.execute(sql_string, (self.producer_id, self.code))

        if self.crown_cur.rowcount == 0:
            return func.HttpResponse("Failed to update producer", headers=global_vars.HEADER, status_code=400)
        else:
            return func.HttpResponse("Successfully updated producer {} to be code {}".format(self.producer_id, self.code), headers={'content-type': 'application/json'}, status_code=201)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        producer_updater = SubmitNewEntry(req)

        if not producer_updater.authenticated:
            return func.HttpResponse(json.dumps(producer_updater.auth_response), headers=global_vars.HEADER, status_code=401)
        elif producer_updater.invalid_params:
            return func.HttpResponse("Missing query params", headers=global_vars.HEADER, status_code=400)
        elif producer_updater.token_missing:
            return func.HttpResponse("Token missing", headers=global_vars.HEADER, status_code=400)
        else:
            return producer_updater.update_producer()

    except Exception:
        error = traceback.format_exc()
        logging.error(error)
        return func.HttpResponse(error, status_code=500)
