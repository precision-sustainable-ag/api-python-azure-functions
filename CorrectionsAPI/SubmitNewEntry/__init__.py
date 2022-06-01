import json
import logging
import os
import traceback

import azure.functions as func

from SharedFunctions import db_connectors, global_vars, initializer


class SubmitNewEntry:
    def __init__(self, req):
        initial_state = initializer.initialize(
            route_params=None, body_params=["data", "asset_name", "id", "xform_id_string", "uid"], req=req)

        self.body_params_obj = initial_state["body_params_obj"]
        self.token = initial_state["token"]
        self.token_missing = initial_state["token"] == None
        self.authenticated = initial_state["authenticated"]
        self.auth_response = initial_state["auth_response"]
        self.invalid_params = initial_state["body_params_obj"] == None

        # connect to dbs
        if self.authenticated:
            self.environment = os.environ.get('AZURE_FUNCTIONS_ENVIRONMENT')
            self.shadow_con, self.shadow_cur, self.shadow_engine = db_connectors.connect_to_shadow(
                self.environment)
            self.mysql_con, self.mysql_cur, self.mysql_engine = db_connectors.connect_to_mysql()

    def insert_new_form(self):
        sql_string = "INSERT INTO kobo (id, asset_name, data, xform_id_string) VALUES (%s, %s, %s, %s)"
        self.mysql_cur.execute(
            sql_string, (self.body_params_obj["id"], self.body_params_obj["asset_name"], self.body_params_obj["data"], self.body_params_obj["xform_id_string"]))

        self.mysql_con.commit()

        return self.mysql_cur.rowcount

    def set_resolved(self):
        sql_string = "UPDATE invalid_row_table_pairs SET resolved = 1 WHERE uid = %s"
        self.shadow_cur.execute(sql_string, (self.body_params_obj["uid"],))

        return self.shadow_cur.rowcount

    def submit_new_entry(self):
        insert_row_count = self.insert_new_form()
        resolved_row_count = self.set_resolved()

        if insert_row_count == 0 or resolved_row_count == 0:
            if insert_row_count == 0 and resolved_row_count == 0:
                return_text = "failed to insert and set resolved"
            elif insert_row_count == 0:
                return_text = "failed to insert %s %s %s %s" % (
                    self.body_params_obj["id"], self.body_params_obj["asset_name"], self.body_params_obj["data"], self.body_params_obj["xform_id_string"])
            else:
                return_text = "failed to set resolved for %s" % self.body_params_obj["uid"]

            return func.HttpResponse(json.dumps({"status": "error", "details": return_text}), headers=global_vars.HEADER, status_code=400)
        else:
            return func.HttpResponse(json.dumps({"status": "success", "details": "successfully inserted new entry with id = %s asset_name = %s data = %s xform_id_string = %s" % (self.body_params_obj["id"], self.body_params_obj["asset_name"], self.body_params_obj["data"], self.body_params_obj["xform_id_string"])}), headers=global_vars.HEADER, status_code=201)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        submittor = SubmitNewEntry(req)

        # authenticate user based on token
        if any([not submittor.authenticated, submittor.invalid_params, submittor.token_missing]):
            return initializer.get_response(submittor.authenticated, submittor.auth_response,
                                            submittor.invalid_params, submittor.token_missing, False)
        else:
            return submittor.submit_new_entry()

    except Exception as error:
        logging.info("program encountered exception: " +
                     traceback.format_exc())
        logging.exception(error)
        return func.HttpResponse(
            json.dumps({"status": "error", "details": traceback.format_exc()}),
            status_code=500,
            headers=global_vars.HEADER
        )
