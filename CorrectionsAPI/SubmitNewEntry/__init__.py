import json
import logging
import os
import traceback

import azure.functions as func

from ..SharedFunctions import authenticator, db_connectors, global_vars


class SubmitNewEntry:
    def __init__(self, req):
        # get params
        try:
            req_body = req.get_json()
        except ValueError:
            self.data = None
            self.asset_name = None
            self.id = None
            self.xform_id_string = None
            self.uid = None
        else:
            self.data = req_body.get('data')
            self.asset_name = req_body.get('asset_name')
            self.id = req_body.get('id')
            self.xform_id_string = req_body.get('xform_id_string')
            self.uid = req_body.get('uid')

        # get token
        try:
            self.token = req.headers.__http_headers__["authorization"].split(" ")[
                1]
            self.token_missing = True if self.token is None else False
        except KeyError:
            self.token_missing = True

        # check for missing missing params
        if None in [self.data, self.asset_name, self.id, self.xform_id_string, self.uid]:
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
            self.mysql_con, self.mysql_cur, self.mysql_engine = db_connectors.connect_to_mysql()

    def insert_new_form(self):
        sql_string = "INSERT INTO kobo (id, asset_name, data, xform_id_string) VALUES (%s, %s, %s, %s)"
        self.mysql_cur.execute(
            sql_string, (self.id, self.asset_name, self.data, self.xform_id_string))

        self.mysql_con.commit()

        return self.mysql_cur.rowcount

    def set_resolved(self):
        sql_string = "UPDATE invalid_row_table_pairs SET resolved = 1 WHERE uid = %s"
        self.shadow_cur.execute(sql_string, (self.uid,))

        return self.shadow_cur.rowcount

    def submit_new_entry(self):
        insert_row_count = self.insert_new_form()
        resolved_row_count = self.set_resolved()

        if insert_row_count == 0 or resolved_row_count == 0:
            if insert_row_count == 0 and resolved_row_count == 0:
                return_text = "Failed to insert and set resolved"
            elif insert_row_count == 0:
                return_text = "Failed to insert"
            else:
                return_text = "Failed to set resolved"

            return func.HttpResponse(return_text, headers=global_vars.HEADER, status_code=400)
        else:
            return func.HttpResponse("Successfully inserted new entry", headers=global_vars.HEADER, status_code=201)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        submittor = SubmitNewEntry(req)

        if not submittor.authenticated:
            return func.HttpResponse(json.dumps(submittor.auth_response), headers=global_vars.HEADER, status_code=401)
        elif submittor.invalid_params:
            return func.HttpResponse("Missing query params", headers=global_vars.HEADER, status_code=400)
        elif submittor.token_missing:
            return func.HttpResponse("Token missing", headers=global_vars.HEADER, status_code=400)
        else:
            return submittor.submit_new_entry()

    except Exception:
        error = traceback.format_exc()
        logging.error(error)
        return func.HttpResponse(error, status_code=500)
