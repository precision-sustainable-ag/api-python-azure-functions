import os
import requests

#  setup connection
BASE_URL = "https://psa-tech-dashboard.auth0.com"

# class variable to avoid repeating the same text
HEADER = {'content-type': 'application/json'}

# method to fetch the Auth0 management API token


def get_management_token():
    # payload and header
    auth0_payload = os.environ["AUTH0_PAYLOAD"]
    auth0_headers = HEADER

    # request token
    auth0_token_res = requests.post(
        BASE_URL + "/oauth/token", data=auth0_payload, headers=auth0_headers)

    # convert to json
    auth0_token_json_data = auth0_token_res.json()

    management_api_token = auth0_token_json_data['access_token']

    return management_api_token

# method to fetch all the Auth0 users info including github token


def get_users(management_api_token):
    # setup management api request
    auth0_users_authorization = "Bearer " + management_api_token
    auth0_users_headers = {'authorization': auth0_users_authorization}

    # request users
    auth0_token_res = requests.get(
        BASE_URL + "/api/v2/users", headers=auth0_users_headers)

    # convert to json
    auth0_users_json_data = auth0_token_res.json()

    return auth0_users_json_data

# method to search for a users github token in auth0_users_json_data


def get_github_tokens(auth0_users_json_data, github_user):
    github_user_token = None
    github_org_owner_token = None
    for user in auth0_users_json_data:
        if user.get("nickname") == github_user:
            github_user_token = user.get("identities")[
                0].get("access_token")
        if user.get("nickname") == "brianwdavis":
            github_org_owner_token = user.get(
                "identities")[0].get("access_token")

    return github_user_token, github_org_owner_token


def generate_auth0_tokens(github_user):
    management_api_token = get_management_token()
    auth0_users_json_data = get_users(management_api_token)

    return get_github_tokens(auth0_users_json_data, github_user)
