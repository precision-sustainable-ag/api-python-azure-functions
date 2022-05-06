import unittest
import azure.functions as func
from requests.structures import CaseInsensitiveDict
import os
import json

from RemoveForm import main  # import the method we want to test
from unittest import mock
from SharedFunctions.set_environment_variables import set_variables
# Note how the class name starts with Test

URL = 'shadow/invalid_row_table_pairs/48'
# Arrange
set_variables()
token = os.environ["USER_TOKEN"]

HEADERS = CaseInsensitiveDict()
HEADERS["Accept"] = "application/json"
HEADERS["Authorization"] = "Bearer {}".format(token)

invalid_token = os.environ["EXPIRED_USER_TOKEN"]

EXPIRED_HEADERS = CaseInsensitiveDict()
EXPIRED_HEADERS["Accept"] = "application/json"
EXPIRED_HEADERS["Authorization"] = "Bearer {}".format(invalid_token)


class TestFetchEditableList(unittest.TestCase):
    def test_good_response(self):
        request = func.HttpRequest(
            method='GET',
            url=URL,
            route_params={'uid': '48'},
            body=None,
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())

        assert response.status_code == 201
        assert json_response.get("status") == "success"
        assert "48" in json_response.get("details")

    def test_invalid_uid(self):
        request = func.HttpRequest(
            method='GET',
            url=URL,
            route_params={'uid': '10000000'},
            body=None,
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 400
        assert "failed to remove form" in json_response["details"]

    def test_no_query_params(self):
        request = func.HttpRequest(
            method='GET',
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
            method='GET',
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
            route_params={'uid': '48'},
            url=URL,
            body=None,
            headers=EXPIRED_HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 401
        assert "token_expired" in str(json_response["details"])
