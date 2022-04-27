import json
import logging
import traceback
import requests

import azure.functions as func

from ..SharedFunctions import authenticator, auth0_functions, global_vars

# github issues class to handle actions on github issues


class AddToTechnicians:
    # constructor sets the user variable
    def __init__(self, req):
        # get params
        self.user = req.route_params.get('user')

        # get token and set flag if it fails
        try:
            self.token = req.headers.__http_headers__["authorization"].split(" ")[
                1]
            self.token_missing = True if self.token is None else False
        except KeyError:
            self.token_missing = True

        # if missing params
        if self.user == None:
            self.invalid_params = True
        else:
            self.invalid_params = False

        # authenticate
        self.authenticated, self.auth_response = authenticator.authenticate(
            self.token)

        # get github tokens
        if self.authenticated:
            self.github_user_token, self.github_org_owner_token = auth0_functions.generate_auth0_tokens(
                self.user)

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

        url = 'https://api.github.com/orgs/precision-sustainable-ag/teams/technicians/memberships/%s' % self.user

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
                    {"Add message": response_obj["add_response"], "Accept message": response_obj["accept_response"]}),
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
        if not technicians_adder.authenticated:
            return func.HttpResponse(json.dumps(technicians_adder.auth_response), headers=global_vars.HEADER, status_code=401)
        elif technicians_adder.invalid_params:
            return func.HttpResponse("Missing query params", headers=global_vars.HEADER, status_code=400)
        elif technicians_adder.token_missing:
            return func.HttpResponse("Token missing", headers=global_vars.HEADER, status_code=400)
        else:
            return technicians_adder.add_to_technicians()

    except Exception as error:
        logging.info("Program encountered exception: " +
                     traceback.format_exc())
        logging.exception(error)
        return func.HttpResponse(
            json.dumps({"Message": traceback.format_exc()}),
            status_code=500,
            headers=global_vars.HEADER
        )
