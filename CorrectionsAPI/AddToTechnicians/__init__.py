import json
import logging
from mimetypes import init
from shutil import ExecError
import traceback
import requests

import azure.functions as func

from SharedFunctions import authenticator, auth0_functions, global_vars, initializer

# github issues class to handle actions on github issues


class AddToTechnicians:
    # constructor sets the user variable
    def __init__(self, req):
        initial_state = initializer.initilize(
            route_params=["user"], body_params=None, req=req)

        self.route_params_obj = initial_state["route_params_obj"]
        self.token = initial_state["token"]
        self.token_missing = initial_state["token"] == None
        self.authenticated = initial_state["authenticated"]
        self.auth_response = initial_state["auth_response"]
        self.invalid_params = initial_state["route_params_obj"] is None

        # get github tokens
        if self.authenticated and not self.invalid_params:
            self.github_user_token, self.github_org_owner_token = auth0_functions.generate_auth0_tokens(
                self.route_params_obj.get("user"))

            self.invalid_user = True if self.github_user_token is None or self.github_org_owner_token is None else False
        else:
            self.invalid_user = True

    def accept_technicians_invite(self):
        url = 'https://api.github.com/user/memberships/orgs/precision-sustainable-ag'

        # Headers
        headers = {
            "Authorization": "token %s" % self.github_user_token,
            "Accept": "application/vnd.github.v3+json"
        }

        data = {"state": "active"}
        payload = json.dumps(data)

        # accept invite
        try:
            response = requests.patch(url, data=payload, headers=headers)
            status = json.loads(response.content.decode())
            print(status)
            return True, status
        except Exception:
            logging.exception(traceback.format_exc())
            return False, "Could not accept org invite " + traceback.format_exc()

    def add_to_technicians(self):
        response_obj = {}

        url = 'https://api.github.com/orgs/precision-sustainable-ag/teams/technicians/memberships/%s' % self.route_params_obj[
            "user"]

        # Headers
        headers = {
            "Authorization": "token %s" % self.github_org_owner_token,
            "Accept": "application/vnd.github.v3+json"
        }

        # add to technicians
        try:
            response = requests.put(url, headers=headers)
            response_obj["add_response"] = json.loads(
                response.content.decode())
            response_obj["add_status"] = True
        except Exception:
            logging.exception(traceback.format_exc())
            response_obj["add_response"] = "Could not add to org " + \
                traceback.format_exc()
            response_obj["add_status"] = False

        accept_status, accept_response = self.accept_technicians_invite()
        response_obj["accept_status"] = accept_status
        response_obj["accept_response"] = accept_response

        if response_obj["add_status"] == True and response_obj["accept_response"]:
            return func.HttpResponse(
                json.dumps(
                    {"add_message": response_obj["add_response"], "accept_message": response_obj["accept_response"]}),
                status_code=201,
                headers=global_vars.HEADER
            )
        else:
            return func.HttpResponse(
                json.dumps(
                    {"Add message": response_obj["add_response"], "Accept message": response_obj["accept_response"]}),
                status_code=400,
                headers=global_vars.HEADER
            )


def main(req: func.HttpRequest) -> func.HttpResponse:
    # log that the function is called
    logging.info('Python HTTP trigger function processed a request.')

    # in a try catch because if the payload is not json it causes exception
    try:
        # instantiate GithupIssues class
        technicians_adder = AddToTechnicians(req)

        # authenticate user based on token
        if any([not technicians_adder.authenticated, technicians_adder.invalid_params, technicians_adder.token_missing, technicians_adder.invalid_user]):
            return initializer.get_response(technicians_adder.authenticated, technicians_adder.auth_response,
                                            technicians_adder.invalid_params, technicians_adder.token_missing, technicians_adder.invalid_user)
        else:
            return technicians_adder.add_to_technicians()

    except Exception as error:
        logging.info("program encountered exception: " +
                     traceback.format_exc())
        logging.exception(error)
        return func.HttpResponse(
            json.dumps({"status": "error", "details": traceback.format_exc()}),
            status_code=500,
            headers=global_vars.HEADER
        )
