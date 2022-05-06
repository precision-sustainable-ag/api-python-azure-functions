import unittest
import azure.functions as func
from requests.structures import CaseInsensitiveDict
import os
import json

from FetchEditableList import main  # import the method we want to test
from unittest import mock
from SharedFunctions.set_environment_variables import set_variables
# Note how the class name starts with Test

URL = 'shadowdb/editable_list/vgaKFRKRg54E2Z7fvayCxf'
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
            route_params={'version': 'vgaKFRKRg54E2Z7fvayCxf'},
            body=None,
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())

        print(json_response)

        assert response.status_code == 201
        assert json_response.get("status") == "success"
        assert json_response.get("entry_to_iterate") == None
        assert "vgaKFRKRg54E2Z7fvayCxf" in json_response.get("details")

        try:
            table_names = json.loads(json_response.get("table_names"))
            assert type(table_names) is list

            iterator_editable_list = json.loads(
                json_response.get("iterator_editable_list"))
            assert type(iterator_editable_list) is list

            editable_list = json.loads(json_response.get("editable_list"))
            assert type(editable_list) is list
        except Exception:
            assert False

    def test_invalid_version(self):
        request = func.HttpRequest(
            method='GET',
            url=URL,
            route_params={'version': 'oansdsdadasd'},
            body=None,
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 400
        assert "no version in shadow db" in json_response["details"]

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
