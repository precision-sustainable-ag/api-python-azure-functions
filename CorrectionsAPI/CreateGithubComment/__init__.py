import json
import logging
import traceback
import requests

import azure.functions as func

from ..SharedFunctions import authenticator, auth0_functions, global_vars

# github issues class to handle actions on github issues


class CreateGithubComment:
    # constructor sets the user variable
    def __init__(self, req):
        # get params from route
        self.user = req.route_params.get('user')
        self.number = req.route_params.get('number')

        # get params from body
        try:
            req_body = req.get_json()
        except ValueError:
            self.comment = None
        else:
            self.comment = req_body.get('comment')

        # get token
        try:
            self.token = req.headers.__http_headers__["authorization"].split(" ")[
                1]
            self.token_missing = True if self.token is None else False
        except KeyError:
            self.token_missing = True

        # check for missing missing params
        if None in [self.user, self.comment, self.number]:
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

    def create_github_comment(self):
        # Create an issue on github.com using the given parameters
        # Url to create issues via POST
        url = 'https://api.github.com/repos/%s/%s/issues/%s/comments' % (
            global_vars.GITHUB_REPO_OWNER, global_vars.GITHUB_REPO_NAME, self.number)

        # Headers
        headers = {
            "Authorization": "token %s" % self.github_user_token,
            "Accept": "application/vnd.github.v3+json"
        }

        # Create our issue working properly, just need to add labels etc
        data = {
            'body': self.comment,
        }
        payload = json.dumps(data)
        # Add the issue to our repository
        response = requests.request("POST", url, data=payload, headers=headers)
        logging.info(str(response.status_code))

        if response.status_code == 201:
            logging.info('Successfully created Comment "%s" on issue #%s' % (
                self.comment, self.number))
            return func.HttpResponse(
                'Successfully created Comment "%s" on issue #%s' % (
                    self.comment, self.number),
                status_code=201,
                headers=global_vars.HEADER
            )
        else:
            logging.info('Could not create Comment "%s"' % self.comment)
            return func.HttpResponse(
                'Could not create Comment "%s"' % self.comment,
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
        if not comment_creator.authenticated:
            return func.HttpResponse(json.dumps(comment_creator.auth_response), headers=global_vars.HEADER, status_code=401)
        elif comment_creator.invalid_params:
            return func.HttpResponse("Missing query params", headers=global_vars.HEADER, status_code=400)
        elif comment_creator.token_missing:
            return func.HttpResponse("Token missing", headers=global_vars.HEADER, status_code=400)
        else:
            return comment_creator.create_github_comment()

    except Exception as error:
        logging.info("Program encountered exception: " +
                     traceback.format_exc())
        logging.exception(error)
        return func.HttpResponse(
            json.dumps({"Message": traceback.format_exc()}),
            status_code=500,
            headers=global_vars.HEADER
        )
