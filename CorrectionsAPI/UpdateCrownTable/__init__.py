import json
import logging
import os
import traceback

import azure.functions as func
from psycopg2 import sql

from SharedFunctions import db_connectors, global_vars, initializer


class UpdateCrownTable:
    def __init__(self, req):
        initial_state = initializer.initialize(
            route_params=["table"], body_params=["values", "conditions"], req=req)

        self.route_params_obj = initial_state["route_params_obj"]
        self.body_params_obj = initial_state["body_params_obj"]
        self.token = initial_state["token"]
        self.token_missing = initial_state["token"] == None
        self.authenticated = initial_state["authenticated"]
        self.auth_response = initial_state["auth_response"]

        print(self.route_params_obj)

        self.invalid_params = initial_state["route_params_obj"] is None or initial_state["body_params_obj"] is None
        self.missing_minimum_identifiers = False

        if not self.invalid_params:
            minimum_identifiers = global_vars.MINIMUM_IDENTIFIERS.get(
                self.route_params_obj["table"])
            self.missing_minimum_identifiers = minimum_identifiers is None or not all(
                item in self.body_params_obj["conditions"].keys() for item in minimum_identifiers)

        print(
            item in minimum_identifiers for item in self.body_params_obj["conditions"].keys())

        # connect to dbs
        if self.authenticated:
            self.environment = os.environ.get('AZURE_FUNCTIONS_ENVIRONMENT')
            self.crown_con, self.crown_cur, self.crown_engine = db_connectors.connect_to_crown(
                self.environment)

    def update_table(self):
        update_prod_query = sql.SQL("UPDATE {table} SET {values} WHERE {identifiers}").format(
            table=sql.Identifier(self.route_params_obj["table"]),
            values=sql.SQL(', ').join(
                sql.Composed([sql.Identifier(k), sql.SQL(" = "), sql.Placeholder(k)]) for k in self.body_params_obj["values"].keys()
            ),
            identifiers=sql.SQL('AND ').join(
                sql.Composed([sql.Identifier(k), sql.SQL(" = "), sql.Placeholder(k)]) for k in self.body_params_obj["conditions"].keys()
            ),
        )

        update_prod_values = self.body_params_obj["values"]
        update_prod_values.update(self.body_params_obj["conditions"])

        print(update_prod_query, dict(update_prod_values))

        self.crown_cur.execute(update_prod_query, dict(update_prod_values))

        if self.crown_cur.rowcount == 0:
            return func.HttpResponse(json.dumps({"status": "error", "details": "failed to update {}".format(self.route_params_obj["table"])}), headers=global_vars.HEADER, status_code=400)
        else:
            return func.HttpResponse(json.dumps({"status": "success", "details": "successfully updated {} to {} with conditions {}".format(self.route_params_obj["table"], json.dumps(self.body_params_obj["values"]), self.body_params_obj["conditions"])}), headers={'content-type': 'application/json'}, status_code=201)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        table_updater = UpdateCrownTable(req)

        # authenticate user based on token
        if any([not table_updater.authenticated, table_updater.invalid_params, table_updater.token_missing, table_updater.missing_minimum_identifiers]):
            return initializer.get_response(table_updater.authenticated, table_updater.auth_response,
                                            table_updater.invalid_params, table_updater.token_missing, False, table_updater.missing_minimum_identifiers)
        else:
            return table_updater.update_table()

    except Exception as error:
        logging.info("program encountered exception: " +
                     traceback.format_exc())
        logging.exception(error)
        return func.HttpResponse(
            json.dumps({"status": "error", "details": traceback.format_exc()}),
            status_code=500,
            headers=global_vars.HEADER
        )
