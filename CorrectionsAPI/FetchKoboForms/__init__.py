import json
import logging
import os
import traceback
import pandas as pd

import azure.functions as func

from SharedFunctions import authenticator, db_connectors, global_vars, initializer


class FetchKoboForms:
    def __init__(self, req):
        initial_state = initializer.initilize(
            route_params=["xform_id_string"], body_params=None, req=req)

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
            self.mysql_con, self.mysql_cur, self.mysql_engine = db_connectors.connect_to_mysql()

    def fetch_bad_uids_data(self, xform_id_string):
        invalid_rows = pd.DataFrame(pd.read_sql(
            "SELECT DISTINCT uid, err, data FROM invalid_row_table_pairs WHERE xform_id_string = '{}' AND resolved = 0".format(xform_id_string), self.shadow_engine))
        return invalid_rows

    def fetch_all_data(self, xform_id_string):
        all_rows = pd.DataFrame(pd.read_sql(
            "SELECT data, uid FROM kobo WHERE xform_id_string = '{}'".format(xform_id_string), self.mysql_engine))
        return all_rows

    def fetch_distinct_uids(self, xform_id_string, resolved):
        distinct_uids = pd.DataFrame(pd.read_sql("SELECT DISTINCT uid, data FROM invalid_row_table_pairs WHERE xform_id_string = '{}' and resolved = '{}'".format(
            xform_id_string, resolved), self.shadow_engine))
        return distinct_uids

    def generate_invalid_rows(self, xform_id_string, history=False):
        if history:
            distinct_uids = self.fetch_distinct_uids(xform_id_string, 1)
        else:
            distinct_uids = self.fetch_distinct_uids(xform_id_string, 0)
        invalid_data = []
        for index, row_entry in distinct_uids.iterrows():
            uid = row_entry.get("uid")
            data = row_entry.get("data")
            errs = pd.DataFrame(pd.read_sql(
                "SELECT DISTINCT err FROM invalid_row_table_pairs WHERE uid = '{}'".format(uid), self.shadow_engine))
            errs_list = []
            for index, row_entry in errs.iterrows():
                errs_list.append(row_entry.get("err"))

            invalid_data.append({"data": data, "errs": errs_list, "uid": uid})

        return invalid_data

    def generate_valid_rows(self):
        invalid_rows = self.fetch_bad_uids_data(
            self.route_params_obj["xform_id_string"])
        all_rows = self.fetch_all_data(
            self.route_params_obj["xform_id_string"])
        valid_list = []

        for index, row_entry in all_rows.iterrows():
            uid = row_entry.get("uid")
            if uid not in invalid_rows.uid.tolist():
                valid_list.append({"data": row_entry.get(
                    "data"), "errs": row_entry.get("err"), "uid": uid})

        return valid_list

    def create_row_object(self):
        uid_history = self.generate_invalid_rows(
            self.route_params_obj["xform_id_string"], True)
        valid_data = self.generate_valid_rows()
        invalid_data = self.generate_invalid_rows(
            self.route_params_obj["xform_id_string"])

        data = {
            "valid_data": valid_data,
            "invalid_data": invalid_data,
            "uid_history": uid_history,
        }

        if not data.get("valid_data") and not data.get("invalid_data"):
            return func.HttpResponse(json.dumps({"status": "error", "details": "no xform_id_string in db"}), headers=global_vars.HEADER, status_code=400)
        else:
            return func.HttpResponse(json.dumps({"status": "success", "kobo_forms": data}), headers=global_vars.HEADER, status_code=201)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        kobo_fetcher = FetchKoboForms(req)

        # authenticate user based on token
        if any([not kobo_fetcher.authenticated, kobo_fetcher.invalid_params, kobo_fetcher.token_missing]):
            return initializer.get_response(kobo_fetcher.authenticated, kobo_fetcher.auth_response,
                                            kobo_fetcher.invalid_params, kobo_fetcher.token_missing, False)
        else:
            return kobo_fetcher.create_row_object()

    except Exception as error:
        logging.info("program encountered exception: " +
                     traceback.format_exc())
        logging.exception(error)
        return func.HttpResponse(
            json.dumps({"status": "error", "details": traceback.format_exc()}),
            status_code=500,
            headers=global_vars.HEADER
        )
