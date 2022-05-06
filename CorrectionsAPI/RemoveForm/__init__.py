import json
import logging
import os
import traceback

import azure.functions as func

from SharedFunctions import authenticator, db_connectors, global_vars, initializer


class RemoveForm:
    def __init__(self, req):
        initial_state = initializer.initilize(
            route_params=["uid"], body_params=None, req=req)

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

    def set_resolved(self):
        sql_string = "UPDATE invalid_row_table_pairs SET resolved = 1 WHERE uid = %s"
        self.shadow_cur.execute(sql_string, (self.route_params_obj["uid"],))

        if self.shadow_cur.rowcount == 0:
            return func.HttpResponse(json.dumps({"status": "error", "details": "failed to remove form"}), headers=global_vars.HEADER, status_code=400)
        else:
            return func.HttpResponse(json.dumps({"status": "success", "details": "successfully deleted row {}".format(self.route_params_obj["uid"])}), headers=global_vars.HEADER, status_code=201)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        remover = RemoveForm(req)

        # authenticate user based on token
        if any([not remover.authenticated, remover.invalid_params, remover.token_missing]):
            return initializer.get_response(remover.authenticated, remover.auth_response,
                                            remover.invalid_params, remover.token_missing, False)
        else:
            return remover.set_resolved()

    except Exception as error:
        logging.info("program encountered exception: " +
                     traceback.format_exc())
        logging.exception(error)
        return func.HttpResponse(
            json.dumps({"status": "error", "details": traceback.format_exc()}),
            status_code=500,
            headers=global_vars.HEADER
        )
