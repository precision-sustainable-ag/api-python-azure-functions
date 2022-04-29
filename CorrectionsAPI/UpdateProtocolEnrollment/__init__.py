import json
import logging
import os
import traceback

import azure.functions as func
from psycopg2 import sql

from ..SharedFunctions import authenticator, db_connectors, global_vars


class UpdateProtocolEnrollment:
    def __init__(self, req):
        # get params from route
        self.code = req.route_params.get('code')

        # get params
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            self.protocols = req_body.get('protocols')

        # get token
        try:
            self.token = req.headers.__http_headers__["authorization"].split(" ")[
                1]
            self.token_missing = True if self.token is None else False
        except KeyError:
            self.token_missing = True

        # check for missing missing params
        if None in [self.code, self.protocols]:
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
        update_prod_query = sql.SQL("UPDATE {table} SET {values} WHERE {identifiers}").format(
            table=sql.Identifier("protocol_enrollment"),
            values=sql.SQL(', ').join(
                sql.Composed([sql.Identifier(k), sql.SQL(" = "), sql.Placeholder(k)]) for k in self.protocols.keys()
            ),
            identifiers=sql.SQL('').join(
                sql.Composed(
                    [sql.Identifier("code"), sql.SQL(" = "), sql.Placeholder("code")])
            ),
        )

        update_prod_values = self.protocols
        update_prod_values["code"] = self.code

        self.crown_cur.execute(update_prod_query, update_prod_values)

        if self.crown_cur.rowcount == 0:
            return func.HttpResponse("Failed to update protocol enrollment", headers=global_vars.HEADER, status_code=400)
        else:
            return func.HttpResponse("Successfully updated protocol_enrollment for code {} to {}".format(self.code, json.dumps(self.protocols)), headers={'content-type': 'application/json'}, status_code=201)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        protocol_updater = UpdateProtocolEnrollment(req)

        if not protocol_updater.authenticated:
            return func.HttpResponse(json.dumps(protocol_updater.auth_response), headers=global_vars.HEADER, status_code=401)
        elif protocol_updater.invalid_params:
            return func.HttpResponse("Missing query params", headers=global_vars.HEADER, status_code=400)
        elif protocol_updater.token_missing:
            return func.HttpResponse("Token missing", headers=global_vars.HEADER, status_code=400)
        else:
            return protocol_updater.update_producer()

    except Exception:
        error = traceback.format_exc()
        logging.error(error)
        return func.HttpResponse(error, status_code=500)
