import json
import logging
import traceback
import requests

import azure.functions as func

from SharedFunctions import auth0_functions, global_vars, initializer

# github issues class to handle actions on github issues


class CreateGithubComment:
    # constructor sets the user variable
    def __init__(self, req):
        initial_state = initializer.initialize(
            route_params=["user", "number"], body_params=["comment"], req=req)

        self.route_params_obj = initial_state["route_params_obj"]
        self.body_params_obj = initial_state["body_params_obj"]
        self.token = initial_state["token"]
        self.token_missing = initial_state["token"] == None
        self.authenticated = initial_state["authenticated"]
        self.auth_response = initial_state["auth_response"]
        self.invalid_params = initial_state["route_params_obj"] == None or initial_state["body_params_obj"] == None

        # get github tokens
        if self.authenticated and not self.invalid_params:
            self.github_user_token, self.github_org_owner_token = auth0_functions.generate_auth0_tokens(
                self.route_params_obj.get("user"))

            self.invalid_user = True if self.github_user_token is None or self.github_org_owner_token is None else False
        else:
            self.invalid_user = True

    def create_github_comment(self):
        # Create an issue on github.com using the given parameters
        # Url to create issues via POST
        url = 'https://api.github.com/repos/%s/%s/issues/%s/comments' % (
            global_vars.GITHUB_REPO_OWNER, global_vars.GITHUB_REPO_NAME, self.route_params_obj.get("number"))

        # Headers
        headers = {
            "Authorization": "token %s" % self.github_user_token,
            "Accept": "application/vnd.github.v3+json"
        }

        # Create our issue working properly, just need to add labels etc
        data = {
            'body': self.body_params_obj["comment"],
        }
        payload = json.dumps(data)
        # Add the issue to our repository
        response = requests.request("POST", url, data=payload, headers=headers)
        logging.info(str(response.status_code))

        if response.status_code == 201:
            return func.HttpResponse(
                json.dumps({"status": "success", "details": 'successfully created Comment "%s" on issue #%s' % (
                    self.body_params_obj["comment"], self.route_params_obj.get("number"))}),
                status_code=201,
                headers=global_vars.HEADER
            )
        else:
            return func.HttpResponse(
                json.dumps({"status": "error", "details": 'could not create comment "%s" on issue #%s' %
                           (self.body_params_obj["comment"], self.route_params_obj["number"])}),
                status_code=400,
                headers=global_vars.HEADER
            )


def main(req: func.HttpRequest) -> func.HttpResponse:
    # log that the function is called
    logging.info('Python HTTP trigger function processed a request.')

    # in a try catch because if the payload is not json it causes exception
    try:
        # instantiate GithupIssues class
        comment_creator = CreateGithubComment(req)

        # authenticate user based on token
        if any([not comment_creator.authenticated, comment_creator.invalid_params, comment_creator.token_missing, comment_creator.invalid_user]):
            return initializer.get_response(comment_creator.authenticated, comment_creator.auth_response,
                                            comment_creator.invalid_params, comment_creator.token_missing, comment_creator.invalid_user)
        else:
            return comment_creator.create_github_comment()

    except Exception as error:
        logging.info("program encountered exception: " +
                     traceback.format_exc())
        logging.exception(error)
        return func.HttpResponse(
            json.dumps({"status": "error", "details": traceback.format_exc()}),
            status_code=500,
            headers=global_vars.HEADER
        )
