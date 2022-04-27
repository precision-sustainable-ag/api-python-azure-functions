import json
import logging
import os
import traceback

import azure.functions as func

from ..SharedFunctions import authenticator, db_connectors, global_vars


class RemoveForm:
    def __init__(self, req):
        # get params from route
        self.uid = req.route_params.get('uid')

        # get token
        try:
            self.token = req.headers.__http_headers__["authorization"].split(" ")[
                1]
            self.token_missing = True if self.token is None else False
        except KeyError:
            self.token_missing = True

        # check for missing missing params
        if self.uid == None:
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

    def set_resolved(self):
        sql_string = "UPDATE invalid_row_table_pairs SET resolved = 1 WHERE uid = %s"
        self.shadow_cur.execute(sql_string, (self.uid,))

        if self.shadow_cur.rowcount == 0:
            return func.HttpResponse("Failed to remove form", headers=global_vars.HEADER, status_code=400)
        else:
            return func.HttpResponse("Successfully deleted row {}".format(self.uid), headers=global_vars.HEADER, status_code=201)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        remover = RemoveForm(req)

        if not remover.authenticated:
            return func.HttpResponse(json.dumps(remover.ath_response), headers=global_vars.HEADER, status_code=401)
        elif remover.invalid_params:
            return func.HttpResponse("Missing query params", headers=global_vars.HEADER, status_code=400)
        elif remover.token_missing:
            return func.HttpResponse("Token missing", headers=global_vars.HEADER, status_code=400)
        else:
            return remover.set_resolved()

    except Exception:
        error = traceback.format_exc()
        logging.error(error)
        return func.HttpResponse(error, status_code=500)
