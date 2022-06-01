import json
import logging
import os
import traceback

import azure.functions as func

from SharedFunctions import db_connectors, global_vars, initializer


class UpdateProtocolEnrollment:
    def __init__(self, req):
        initial_state = initializer.initialize(
            route_params=None, body_params=["code"], req=req)

        self.body_params_obj = initial_state["body_params_obj"]
        self.token = initial_state["token"]
        self.token_missing = initial_state["token"] == None
        self.authenticated = initial_state["authenticated"]
        self.auth_response = initial_state["auth_response"]
        self.invalid_params = initial_state["body_params_obj"] is None

        # connect to dbs
        if self.authenticated:
            self.environment = os.environ.get('AZURE_FUNCTIONS_ENVIRONMENT')
            self.crown_con, self.crown_cur, self.crown_engine = db_connectors.connect_to_crown(
                self.environment)

    def update_producer(self):
        insert_prod_query = "INSERT INTO protocol_enrollment (farm_history, in_field_biomass, decomp_biomass, soil_texture, cash_crop_yield, weed_quadrat_photos_beta, bulk_density, soil_nitrogen, gps_locations, sensor_data, code, weed_visual_rating, corn_disease, yield_monitor) values (1, 1, 1, 1, 1, 0, 0, 0, 1, 1, %s, 0, 0, 0)"

        try:
            self.crown_cur.execute(
                insert_prod_query, (self.body_params_obj["code"],))
            if self.crown_cur.rowcount == 0:
                return func.HttpResponse(json.dumps({"status": "error", "details": "failed to insert code {} into protocol enrollment".format(self.body_params_obj["code"])}), headers=global_vars.HEADER, status_code=400)
            else:
                return func.HttpResponse(json.dumps({"status": "success", "details": "successfully inserted code {} into protocol_enrollment".format(self.body_params_obj["code"])}), headers={'content-type': 'application/json'}, status_code=201)
        except Exception:
            return func.HttpResponse(json.dumps({"status": "error", "details": "failed to insert code {} into protocol enrollment".format(self.body_params_obj["code"])}), headers=global_vars.HEADER, status_code=400)


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
