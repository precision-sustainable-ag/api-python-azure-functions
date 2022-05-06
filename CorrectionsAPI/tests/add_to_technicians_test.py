import unittest
import azure.functions as func
from requests.structures import CaseInsensitiveDict
import os
import json

from AddToTechnicians import main  # import the method we want to test
from unittest import mock
from SharedFunctions.set_environment_variables import set_variables
# Note how the class name starts with Test

URL = 'precision-sustainable-ag/teams/technicians'

set_variables()
token = os.environ["USER_TOKEN"]

HEADERS = CaseInsensitiveDict()
HEADERS["Accept"] = "application/json"
HEADERS["Authorization"] = "Bearer {}".format(token)

invalid_token = os.environ["EXPIRED_USER_TOKEN"]

EXPIRED_HEADERS = CaseInsensitiveDict()
EXPIRED_HEADERS["Accept"] = "application/json"
EXPIRED_HEADERS["Authorization"] = "Bearer {}".format(invalid_token)


class TestAddToTechnicians(unittest.TestCase):
    def test_good_response(self):
        request = func.HttpRequest(
            method='POST',
            url=URL,
            route_params={'user': 'mikahpinegar'},
            body=None,
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())

        print(json_response)

        assert response.status_code == 201
        assert json_response["add_message"]["state"] == "active"
        assert json_response["accept_message"]["state"] == "active"

    def test_bad_invalid_github_user(self):
        request = func.HttpRequest(
            method='POST',
            url=URL,
            route_params={'user': 'oansddasd', 'number': '495'},
            body=None,
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 400
        assert "invalid github nickname" in json_response["details"]

    def test_no_query_params(self):
        request = func.HttpRequest(
            method='POST',
            url=URL,
            body=None,
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 400
        assert "missing query params" in json_response["details"]

    def test_no_token(self):
        request = func.HttpRequest(
            method='POST',
            route_params={'user': 'mikahpinegar'},
            url=URL,
            body=None,
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 401
        assert "token missing" in json_response["details"]

    def test_expired_token(self):
        request = func.HttpRequest(
            method='POST',
            route_params={'user': 'mikahpinegar'},
            url=URL,
            body=None,
            headers=EXPIRED_HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 401
        assert "token_expired" in str(json_response["details"])
