import http.client
import json
import os

#  setup connection
auth0_connection = http.client.HTTPSConnection(
    "psa-tech-dashboard.auth0.com")

# class variable to avoid repeating the same text
HEADER = {'content-type': 'application/json'}

# method to fetch the Auth0 management API token


def get_token():
    # payload and header
    auth0_payload = os.environ["AUTH0_PAYLOAD"]
    auth0_headers = HEADER
    # request token
    auth0_connection.request(
        "POST", "/oauth/token", auth0_payload, auth0_headers)
    auth0_token_res = auth0_connection.getresponse()
    auth0_token_data = auth0_token_res.read()
    # convert to json
    json_auth0_token_data = auth0_token_data.decode('utf8')
    auth0_token_json_data = json.loads(json_auth0_token_data)

    management_api_token = auth0_token_json_data['access_token']

    return management_api_token

# method to fetch all the Auth0 users info including github token


def get_users(management_api_token):
    # setup management api request
    auth0_users_authorization = "Bearer " + management_api_token
    auth0_users_headers = {'authorization': auth0_users_authorization}

    # request users
    auth0_connection.request(
        "GET", "/api/v2/users", headers=auth0_users_headers)
    auth0_users_res = auth0_connection.getresponse()
    auth0_users_data = auth0_users_res.read()

    # convert to json
    json_auth0_users_data = auth0_users_data.decode('utf8')
    auth0_users_json_data = json.loads(json_auth0_users_data)

    return auth0_users_json_data

# method to search for a users github token in auth0_users_json_data


def get_github_tokens(auth0_users_json_data, github_user):
    for user in auth0_users_json_data:
        if user.get("nickname") == github_user:
            github_user_token = user.get("identities")[
                0].get("access_token")
        if user.get("nickname") == "brianwdavis":
            github_org_owner_token = user.get(
                "identities")[0].get("access_token")

    return github_user_token, github_org_owner_token


def generate_auth0_tokens(github_user):
    management_api_token = get_token()
    auth0_users_json_data = get_users(management_api_token)

    return get_github_tokens(auth0_users_json_data, github_user)
